// Copyright 2009 The Go Authors. All rights reserved.
// Use of this source code is governed by a BSD-style
// license that can be found at the end of this file.
package main
import "fmt"

// Send the sequence 2, 3, 4, ... to channel ch.
func generate(ch chan int) {
	for i := 2; i<300; i++ {
		ch <- i // Send i to channel ch.
	}
	close(ch)
}

// Copy the values from channel in to channel out,
// removing those divisible by prime.
func filter(in, out chan int, prime int) {
	for {
		i, ok := <-in
		if !ok {
		  close(out)
		  break
		}
		if i%prime != 0 {
			// Receive value of new variable i from in.
			out <- i // Send i to channel out.
		}
	}
}

// The prime sieve: Daisy-chain filter processes together.
func main() {
	ch := make(chan int) // Create a new channel.
	go generate(ch) // Start generate() as a goroutine.
	for {
		prime, ok := <-ch
		if !ok {
		  break
		}
		fmt.Print(prime, " ")
		ch1 := make(chan int)
		go filter(ch, ch1, prime)
		ch = ch1
	}
}


/*
Copyright © 2009 The Go Authors. All rights reserved.
 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are
 met:
    * Redistributions of source code must retain the above copyright
 notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above
 copyright notice, this list of conditions and the following disclaimer
 in the documentation and/or other materials provided with the
 distribution.
    * Neither the name of Google Inc. nor the names of its
 contributors may be used to endorse or promote products derived from
 this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

 Subject to the terms and conditions of this License, Google hereby
 grants to You a perpetual, worldwide, non-exclusive, no-charge,
 royalty-free, irrevocable (except as stated in this section) patent
 license to make, have made, use, offer to sell, sell, import, and
 otherwise transfer this implementation of Go, where such license
 applies only to those patent claims licensable by Google that are
 necessarily infringed by use of this implementation of Go. If You
 institute patent litigation against any entity (including a
 cross-claim or counterclaim in a lawsuit) alleging that this
 implementation of Go or a Contribution incorporated within this
 implementation of Go constitutes direct or contributory patent
 infringement, then any patent licenses granted to You under this
 License for this implementation of Go shall terminate as of the date
 such litigation is filed.
*/
