package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"path"
)

func main() {
	// disable showing time with log failures
	log.SetFlags(0)

	if len(os.Args) > 1 && os.Args[1] == "edit" {
		spawnEditor()
		return
	}

	remotes := loadConfig()

	remote, shouldConnect := selectRemote(remotes)

	if shouldConnect {
		ssh(remote)
	}
}

func spawnEditor() {
	editor := os.Getenv("EDITOR")

	if editor == "" {
		log.Fatalf("EDITOR environment variable not defined\n")
	}

	fmt.Println("Opening config file in your $EDITOR")
	fmt.Println("The config file is a JSON array of objects like: [{\"nn\": \"Server 1\", \"un\": \"root\", \"hn\": \"192.168.1.200\"}]")
	fmt.Println("Where 'nn' = nickname, 'un' = username, 'hn' = host name")
	fmt.Println("Press Enter to continue...")

	bufio.NewReader(os.Stdin).ReadBytes('\n')

	cmd := exec.Command(editor, getConfigFilePath())

	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Run()
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

func getConfigFilePath() string {
	configDir, err := os.UserConfigDir()

	if err != nil {
		log.Fatal("Error getting config dir", err)
	}

	return path.Join(configDir, "sheodox/sshmon/servers.json")
}

func loadConfig() []RemoteConfig {
	config := make([]RemoteConfig, 0)
	configFilePath := getConfigFilePath()

	configBytes, err := os.ReadFile(configFilePath)

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
