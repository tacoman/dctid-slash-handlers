package main

import (
    "encoding/json"
    "net/http"
    "log"
    "os"

    "github.com/aws/aws-lambda-go/events"
    "github.com/aws/aws-lambda-go/lambda"
)

var errorLogger = log.New(os.Stderr, "ERROR ", log.Llongfile)

type text struct {
    Type   string `json:"type"`
    Text   string `json:"text"`
}

type block struct {
    Type   string `json:"type"`
    Text   text `json:"text"`
}

type blockcontainer struct {
    Blocks []block `json:"blocks"`
    ResponseType string `json:"response_type"`
}

func show(req events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
    blocks := blockcontainer {
            ResponseType: "in_channel",
            Blocks: []block{
                block {
                    Type:   "section",
                    Text:  text {
                        Type: "mrkdwn",
                        Text: "test date is *2020-03-10*",
                    },
                },
    }, 
    }

    js, err := json.Marshal(blocks)
    if err != nil {
        return serverError(err)
    }

    return events.APIGatewayProxyResponse{
        StatusCode: http.StatusOK,
        Headers: map[string]string{
                "Content-Type":           "application/json",
        },
        Body:       string(js),
    }, nil
}

// Add a helper for handling errors. This logs any error to os.Stderr
// and returns a 500 Internal Server Error response that the AWS API
// Gateway understands.
func serverError(err error) (events.APIGatewayProxyResponse, error) {
        errorLogger.Println(err.Error())
    
        return events.APIGatewayProxyResponse{
            StatusCode: http.StatusInternalServerError,
            Body:       http.StatusText(http.StatusInternalServerError),
        }, nil
    }
    
    // Similarly add a helper for send responses relating to client errors.
    func clientError(status int) (events.APIGatewayProxyResponse, error) {
        return events.APIGatewayProxyResponse{
            StatusCode: status,
            Body:       http.StatusText(status),
        }, nil
    }
    

func main() {
    lambda.Start(show)
}
