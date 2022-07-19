package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
)

func main() {
	port := ":5001"
	proxy1 := os.Getenv("PROXY_ONE")
	proxy2 := os.Getenv("PROXY_TWO")
	fmt.Printf("(proxy1: %v \nproxy2: %v\n", proxy1, proxy2)

	mainServer := http.NewServeMux()
	// handle all requests to your server using the proxy
	mainServer.HandleFunc("/", ProxyRequestHandler(proxy1, proxy2))
	fmt.Printf("started main server on port: %s \n", port)
	log.Fatal(http.ListenAndServe(port, mainServer))
}

// ProxyRequestHandler handles the http request using proxy
func ProxyRequestHandler(proxy1, proxy2 string) func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		fmt.Println("new req")
		body, _ := ioutil.ReadAll(r.Body)
		fmt.Printf("%s \n", body)
		var jBody map[string]interface{}
		err := json.Unmarshal(body, &jBody)

		if err != nil {
			fmt.Printf("error during json unmarshal %s \n", err)
			w.WriteHeader(http.StatusBadRequest)
			w.Write([]byte("cant parse"))
			return
		}

		if _, ok := jBody["update_id"]; !ok{
			fmt.Println("no update_id in body")
			w.WriteHeader(http.StatusBadRequest)
			w.Write([]byte("cant parse"))
			return
		}

		if _, err := http.Post(proxy1, "application/json", bytes.NewBuffer(body)); err != nil {
			fmt.Printf("proxy1 post err: %v \n", err)
		}

		if _, err = http.Post(proxy2, "application/json", bytes.NewBuffer(body)); err != nil {
			fmt.Printf("proxy2 post err: %v \n", err)
		}
		w.Write([]byte("ok"))
	}
}
