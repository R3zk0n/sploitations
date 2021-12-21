package main

import (
	"bytes"
	"fmt"
	"github.com/akamensky/argparse"
	"github.com/fatih/color"
	"howett.net/plist"
	"io/ioutil"
	"os"
	"path/filepath"
)





func check(e error) {
	if e != nil {
		panic(e)
	}
}


// Some reason that a dict isnt a type..
type dictionary = map[string]interface{}

// Colors

// Structs.
type MachParse struct {
	// String -> CFString
	// Int -> CFNumber
	// real -> CF...
	// date -> CFData
	// Array -> CFArray
	// Dict -> CFDict
	// Can we use a linked list to parse this, eg [data | node ] (1) --> [data | node] (2) --> [data | node] (3)
	DaemonName string `plist:"Label"`
	RunAtLoad bool `plist:"RunAtLoad"`
	Program string`plist:"Program"`
	User string`plist:"UserName"`
	Groupname string `plist:"GroupName"`
	ProgramArgs [1024]string `plist:"ProgramArguments"`
	EnvVar dictionary`plist:"EnvironmentVariables"`
	MachNames dictionary`plist:"MachServices"`
	Global dictionary`plist:"Version4"`

}



func removeEmptyStrings(s [1024]string) []string {
	var r []string
	for _, str := range s {
		if str != "" {
			r = append(r, str)
		}
	}
	return r
}

func read_plist_dir(Directory string){
	files, err := ioutil.ReadDir(Directory)
	check(err)
	fmt.Println("Directory: ", Directory)
	for _, file := range files {
		fileExt := filepath.Ext(file.Name())
		if fileExt != ".plist" {
			print("Invaild File\n")
		} else {
			println(file.Name())
			read_file, err := os.Open("/System/Library/LaunchDaemons/" + file.Name())
			check(err);
			read_plist(read_file)





		}
	}
}



func createKeyValuePairs(m map[string]string) string {
	b := new(bytes.Buffer)
	for key, value := range m {
		fmt.Fprintf(b, "%s=\"%s\"\n", key, value)
	}
	return b.String()
}



func read_plist(read *os.File) {
	b_underline := color.New(color.FgCyan)
	r_underline := color.New(color.FgRed).Add(color.Underline)
	yellow := color.New(color.FgYellow)
	green_bold := color.New(color.FgGreen).Add(color.Bold)
	purple := color.New(color.FgHiMagenta)
	var PlistStruct MachParse
	decoder := plist.NewDecoder(read)
	err := decoder.Decode(&PlistStruct)

	if err != nil {
		fmt.Println(err)
	}
	// JetStream Parsing.// Jetstream is annoying..



//	SystemXPCServices := PlistStruct.Global["SystemXPCService"].(map[string]interface {})

	///var result dictionary


//
		//for _, value := range SystemXPCServices{
		//	}
			purple.Println("==========================================")
			ProgramArgs := removeEmptyStrings(PlistStruct.ProgramArgs)
			fmt.Printf("Program Arguments: %s\n", ProgramArgs)

			if PlistStruct.RunAtLoad == true {
				r_underline.Println("Runs at Load: Yes")
			} else {
				fmt.Println("Runs at Load: No")
			}
			if PlistStruct.Program != "" {
				fmt.Println("Program: " + PlistStruct.Program)

			}

			if PlistStruct.User != "" {
				fmt.Println("UserName: " + PlistStruct.User)

			}
			if PlistStruct.DaemonName != "" {
				yellow.Println("DaemonName: " + PlistStruct.DaemonName)
			}

			for k_key, _ := range PlistStruct.EnvVar {
				green_bold.Println("Environment Variables:", k_key)
			}

			for key, _ := range PlistStruct.MachNames {
				b_underline.Println("Mach Service: " + key)
			}
		}
// Main
func main() {
	/// Setup
	//Colors
	purple := color.New(color.FgHiMagenta)
	parser := argparse.NewParser("print", "Prints provided string to stdout")
	// Create string flag
	s := parser.String("f", "file", &argparse.Options{Required: false, Help: "File to scan"})
	d := parser.String("d", "directory", &argparse.Options{Required: false, Help: "Directory to scan .plists"})

	// Parse input
	err := parser.Parse(os.Args)
	if err != nil {
		// In case of error print error and print usage
		// This can also be done by passing -h or --help flags
		fmt.Print(parser.Usage(err))
	}
	purple.Println("==========================================")

	fmt.Println(*s)

	if *d != "" {
		read_plist_dir(*d)
	}
	if *s != "" {
		read, err := os.Open(*s)
		if err != nil {
			panic("Unable to open")
		}

		read_plist(read)
	}

}
