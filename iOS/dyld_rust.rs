use object::macho::{DyldCacheHeader, DyldCacheImageInfo};
use object::read::macho::{address_to_file_offset, DyldCache, DyldCacheImage};
use object::{Architecture, Endian, Endianness, ReadRef, U32};
use std::ffi::{CStr, CString};
use std::fs::{File, OpenOptions};
use std::{env, fs, process};
use std::io::{BufReader, Write}; // bring trait into scope
#[macro_use]
use std::os;
use block::{Block, ConcreteBlock};
use clap::Parser;
use libc::*;
use libloading::{Library, Symbol};
use object::archive::Header;
use object::read::macho;
use object::SymbolKind::Null;
use regex::Regex;
use std::path::{Path, PathBuf};
use std::ptr::null;
use std::str;
#[derive(Parser, Debug)]
#[clap(author = "Rezkon")]
#[clap(version = "zeta 0.0.1")]
#[clap(long_about = None)]
struct Flags {
   //TODO #[clap(short = 's', parse(try_from_str))]
   //TODO SymbolSearch: Option<String>,
    #[clap(short = 'l', parse(try_from_str))]
    /// The cache path to list the frameworks..
    cache_path_location: Option<String>,
    /// The shared cache file to extract from
    #[clap(short = 'i', value_name = "input")]
    #[clap(parse(from_os_str))]
    shared_cache_path: Option<PathBuf>,
    /// The root output directory for the extracted libraries
    #[clap(parse(from_os_str))]
    #[clap(short = 'o', value_name = "output")]
    output_path: Option<PathBuf>,
}
fn fail<S: Into<String>>(message: S) -> ! {
    eprintln!("{}", message.into());
    std::process::exit(1)
}
fn path_to_cstring(path: PathBuf) -> CString {
    use std::os::unix::ffi::OsStrExt;
    CString::new(path.as_os_str().as_bytes()).unwrap()
}
fn extract_shared_cache(library_path: PathBuf, input_path: CString, output_path: CString) {
    let Path = "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/usr/lib/dsc_extractor.bundle";
    let mut Dream = PathBuf::from(String::from_utf8(Vec::from(Path)).unwrap().trim());
    println!("Extracting Shared Cache : {}", Dream.to_str().unwrap());
    let progress_block = ConcreteBlock::new(|x, y| println!("Extracted Frameworks {}/{}", x, y));
    unsafe {
        let library = Library::new(library_path).unwrap();
        println!("Library Loaded: {:?}", library);
        let func: Symbol<
            unsafe extern "C" fn(
                input_path: *const c_char,
                output_path: *const c_char,
                progress: &Block<(usize, usize), ()>,
            ),
        > = library
            .get(b"dyld_shared_cache_extract_dylibs_progress")
            .unwrap();
        func(input_path.as_ptr(), output_path.as_ptr(), &progress_block);
    }
}
fn symbol_check(input_path: CString, output_path: CString, Symbol: &str) {
    let Path = "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/usr/lib/dsc_extractor.bundle";
    let mut Path_Inc = PathBuf::from(String::from_utf8(Vec::from(Path)).unwrap().trim());
    let c_str = CString::new(Path).unwrap();
    let c_path: *const c_char = c_str.as_ptr() as *const c_char;
    let shared_cache_symbol = "dyld_shared_cache_extract_dylibs_progress";
    let c_str = CString::new(Symbol).unwrap();
    let c_symbols: *const c_char = c_str.as_ptr() as *const c_char;
    let mut handle = unsafe { libc::dlopen(c_path, RTLD_LAZY) };
    let extract = unsafe { dlsym(handle, c_symbols) };
    println!("Found dyld_cache_extract_symbol: {:?}", extract);
    if extract.is_null() {
        println!("[XXXXX] Error we have no handle! [XXXXX]");
    }
    extract_shared_cache(Path_Inc, input_path, output_path);
}
fn list_frameworks(file_path: String) {
    let arg_len = file_path.len();
    for file_path in env::args().skip(2) {
        if arg_len != 0 {
            println!();
            println!("{}:", file_path);
        }
        let file = match fs::File::open(&file_path) {
            Ok(file) => file,
            Err(err) => {
                println!("Failed to open file '{}': {}", file_path, err);
                continue;
            }
        };
        let subcache_files = open_subcaches_if_exist(&file_path);
        let file = match unsafe { memmap2::Mmap::map(&file) } {
            Ok(mmap) => mmap,
            Err(err) => {
                println!("Failed to map file '{}': {}", file_path, err,);
                continue;
            }
        };
        ///TODO: Information Dumping of the Dyld cache header, For some reason. It seems to have issues on the u32 structures.
        ///
        let header = DyldCacheHeader::<Endianness>::parse(&*file);
        let header_type = std::str::from_utf8(&header.unwrap().magic).unwrap();
        let uuid = header.unwrap().images_count.get(Default::default());
        let image_count: u32 = header.unwrap().images_count.get(Default::default());
        let mapping_count: u32 = header.unwrap().mapping_count.get(Default::default());
        print!(
            "================ Header Info========================
            \nHeader: {} Image Count: {} Mappings: {}\n",
            header_type, image_count, mapping_count
        );
        let subcache_files: Option<Vec<_>> = subcache_files
            .into_iter()
            .map(
                |subcache_file| match unsafe { memmap2::Mmap::map(&subcache_file) } {
                    Ok(mmap) => Some(mmap),
                    Err(err) => {
                        eprintln!("Failed to map file '{}': {}", file_path, err);
                        None
                    }
                },
            )
            .collect();
        let subcache_files: Vec<&[u8]> = match &subcache_files {
            Some(subcache_files) => subcache_files
                .iter()
                .map(|subcache_file| &**subcache_file)
                .collect(),
            None => continue,
        };
        let cache = match DyldCache::<Endianness>::parse(&*file, &subcache_files) {
            Ok(cache) => cache,
            Err(err) => {
                println!(
                    "Failed to parse Dyld shared cache file '{}': {}",
                    file_path, err,
                );
                continue;
            }
        };
        // Print the list of image paths in this file.
        for image in cache.images() {
            if let Ok(path) = image.path() {
                for offset in image.image_data_and_offset() {
                    println!("{}:  0x7fff{:x}", path, offset.1);
                    //TODO: Implement regex checking of private frameworks
                }
            }
        }
    }
}
fn main() {
    let Opts = Flags::parse();
    if let Some(cache_path_location) = Opts.cache_path_location.as_deref() {
        println!("Input: {:?}", cache_path_location.to_string());
        list_frameworks("/".to_string());
    }
    if let Some(shared_cache_path) = Opts.shared_cache_path.as_deref() {
        if let Some(output_path) = Opts.output_path.as_deref() {
                println!("Input: {:?}", shared_cache_path);
                println!("Output: {:?}", output_path);
                symbol_check(
                    path_to_cstring(shared_cache_path.to_path_buf()),
                    path_to_cstring(output_path.to_path_buf()),"dyld_shared_cache_extract_dylibs_progress"
            );
        }
    }
}
// If the file is a dyld shared cache, and we're on macOS 12 or later,
// then there will be one or more "subcache" files next to this file,
// with the names filename.1, filename.2, ..., filename.symbols.
fn open_subcaches_if_exist(path: &str) -> Vec<fs::File> {
    let mut files = Vec::new();
    for i in 1.. {
        let subcache_path = format!("{}.{}", path, i);
        match fs::File::open(&subcache_path) {
            Ok(subcache_file) => files.push(subcache_file),
            Err(_) => break,
        };
    }
    let symbols_subcache_path = format!("{}.symbols", path);
    if let Ok(subcache_file) = fs::File::open(&symbols_subcache_path) {
        files.push(subcache_file);
    };
    println!("Found {} subcache files", files.len());
    files
}
