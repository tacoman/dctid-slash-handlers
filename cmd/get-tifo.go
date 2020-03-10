package main
 
import (
        "github.com/aws/aws-lambda-go/lambda"
)

type MyResponse struct {
	Message string `json:"Answer:"`
}
 
func HandleLambdaEvent() (MyResponse, error) {
        return MyResponse{Message: "It worked!"}, nil
}
 
func main() {
        lambda.Start(HandleLambdaEvent)
}