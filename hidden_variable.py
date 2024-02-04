# import ngrok python sdk
import ngrok


token = "2btYGLUxxjlnePRLvIYi2MboZw5_6UFFZgH1HF726wKrXU8yM"
API_KEY = "6817836139:AAGs17tJAy3h4ZigESutvVkx-5gNMITo-VY" # dtb
_update_ = {
    "update":"webhook integration-1",
    "description":"webhook integration was done for scaling the bot for large number of users.[30/01/2024]"
}

listener = ngrok.forward("localhost:8443", authtoken=token)
URL = listener.url()


