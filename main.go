package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"path"
	"strconv"
)

func main() {
	// disable showing time with log failures
	log.SetFlags(0)

	config := loadConfig()

	fmt.Println("Enter the number of a remote you want to connect to:")

	for index, remote := range config {
		fmt.Printf("%v. %v - %v@%v\n", index+1, remote.Nickname, remote.Username, remote.Hostname)
	}

	fmt.Print("> ")
	var choice string
	_, err := fmt.Scanln(&choice)
	if err != nil {
		log.Fatal("Error getting choice", err)
	}

	choiceNum, err := strconv.Atoi(choice)

	if err != nil {
		log.Fatal("Error parsing choice", err)
	}

	choiceIndex := choiceNum - 1

	if choiceIndex < 0 || choiceIndex >= len(config) {
		log.Fatalf("%v is out of bounds, must be between 1 and %v\n", choiceNum, len(config))
	}
	// prompted using position, need to subtract to get index
	remote := config[choiceIndex]

	ssh(remote)
}

func ssh(remote RemoteConfig) {
	connectionString := fmt.Sprintf("%v@%v", remote.Username, remote.Hostname)
	fmt.Printf("\nConnecting to %v\n", remote.Nickname)
	fmt.Printf("> ssh %v\n", connectionString)
	cmd := exec.Command("ssh", connectionString)

	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Run()
}

type RemoteConfig struct {
	Nickname string `json:"nn"`
	Username string `json:"un"`
	Hostname string `json:"hn"`
}

func loadConfig() []RemoteConfig {
	configDir, err := os.UserConfigDir()

	if err != nil {
		log.Fatal("Error getting config dir", err)
	}

	config := make([]RemoteConfig, 0)
	configFilePath := path.Join(configDir, "sheodox/sshmon/servers.json")

	configBytes, err := ioutil.ReadFile(configFilePath)

	if err != nil {
		log.Fatal("Error reading config file", err)
	}

	// load config
	err = json.Unmarshal(configBytes, &config)

	if err != nil {
		log.Fatal("Error parsing config file", err)
	}

	return config
}
