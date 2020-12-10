package main

import (
	"fmt"
	"os"
	"runtime"
	"strconv"

	"io/ioutil"
	"os/exec"

	"github.com/gammazero/workerpool"
)

func main() {
	PythonPath := os.Args[1]

	testsCount := 300
	wp := workerpool.New(runtime.NumCPU() - 1)

	for i := 1; i <= testsCount; i++ {
		systemID := strconv.Itoa(i)
		wp.Submit(func() {
			fmt.Println("starting ", systemID)
			doneFile := "dones/" + systemID

			if _, err := os.Stat(doneFile); os.IsNotExist(err) {
				os.Remove("./results/" + systemID + ".txt")
				cmd := exec.Command(PythonPath, "main.py", systemID)
				err := cmd.Run()
				if err != nil {
					fmt.Println(err)
				}
				e := ioutil.WriteFile(doneFile, []byte("done"), 0644)
				if e != nil {
					panic(e)
				}
			}
			fmt.Println(systemID, "done!")
		})
	}

	wp.StopWait()
}
