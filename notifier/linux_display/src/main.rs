use anyhow::Result;
use clap::Parser;
use serde::{Deserialize, Serialize};
use std::path::Path;
use tokio::{
    io::{AsyncReadExt, AsyncWriteExt},
    net::{UnixListener, UnixStream},
    process::Command,
};

#[derive(Parser, Debug)]
#[command(about = "A simple service for execution shell commands via unix service")]
struct Config {
    #[arg(
        long,
        env = "SG_DISPLAY_SOCKET",
        default_value = "/tmp/display_notification_rc.sock"
    )]
    socket: String,

    #[arg(long, env = "DN_DEBUG", default_value_t = false)]
    debug: bool,
}
impl Config {
    fn new() -> Self {
        Config::parse()
    }
}

#[derive(Debug, Serialize, Deserialize)]
struct NotifyCommand {
    cmd: String,
    title: String,
    message: String,
}

impl NotifyCommand {
    fn new(cmd: String, title: String, message: String) -> Self {
        Self {
            cmd,
            title,
            message,
        }
    }

    // Serialize to JSON bytes
    fn to_bytes(&self) -> Result<Vec<u8>> {
        let json = serde_json::to_string(self)?;
        Ok(json.into_bytes())
    }

    // Deserialize from JSON bytes
    fn from_bytes(bytes: &[u8]) -> Result<Self> {
        let json_str = std::str::from_utf8(bytes)?;
        let command = serde_json::from_str(json_str)?;
        Ok(command)
    }
}

struct UnixSocketServer {
    socket_path: String,
}

impl UnixSocketServer {
    fn new(socket_path: String) -> Self {
        Self { socket_path }
    }

    async fn start(&self) -> Result<()> {
        // Remove socket file if it exists
        println!("socket_path={}", self.socket_path);

        let _ = tokio::fs::remove_file(&self.socket_path).await;

        // Create parent directory if it doesn't exist
        if let Some(parent) = Path::new(&self.socket_path).parent() {
            tokio::fs::create_dir_all(parent).await?;
        }

        // Bind to the Unix socket
        let listener = UnixListener::bind(&self.socket_path)?;
        println!("Server listening on: {}", self.socket_path);

        loop {
            // Accept incoming connections
            let (stream, _) = listener.accept().await?;
            println!("New client connected");

            // Handle each connection in a separate task
            let socket_path = self.socket_path.clone();
            tokio::spawn(async move {
                if let Err(e) = Self::handle_client(stream, socket_path).await {
                    eprintln!("Error handling client: {}", e);
                }
            });
        }
    }

    async fn handle_client(mut stream: UnixStream, socket_path: String) -> Result<()> {
        let mut buffer = vec![0; 1024];

        loop {
            // Read data from the client
            match stream.read(&mut buffer).await {
                Ok(0) => {
                    // Client disconnected
                    println!("Client disconnected");
                    break;
                }
                Ok(n) => {
                    // Process the received data
                    let received_data = &buffer[..n];

                    match NotifyCommand::from_bytes(received_data) {
                        Ok(command) => {
                            println!("Received command: {:?}", command);

                            // Process the command based on cmd field
                            let response = Self::process_command(&command).await;

                            // Send response back to client
                            if let Err(e) = stream.write_all(&response).await {
                                eprintln!("Failed to send response: {}", e);
                                break;
                            }
                        }
                        Err(e) => {
                            eprintln!("Failed to parse command: {}", e);
                            let error_response = format!("Error: Invalid command format - {}", e);
                            let _ = stream.write_all(error_response.as_bytes()).await;
                        }
                    }
                }
                Err(e) => {
                    eprintln!("Error reading from socket: {}", e);
                    break;
                }
            }
        }

        Ok(())
    }

    async fn process_command(command: &NotifyCommand) -> Vec<u8> {
        match command.cmd.as_str() {
            "NOTIFY" => {
                println!("Processing NOTIFY command:");
                println!("  Title: {}", command.title);
                println!("  Message: {}", command.message);

                match Command::new("notify-send")
                    .arg(command.title.as_str())
                    .arg(command.message.as_str())
                    .status()
                    .await
                {
                    Ok(_) => "Ok".as_bytes().to_vec(),
                    Err(e) => {
                        eprintln!("Error in command execution: {}", e);
                        "Err".as_bytes().to_vec()
                    }
                }
            }
            _ => {
                let response = format!("Unknown command: {}", command.cmd);
                response.as_bytes().to_vec()
            }
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    let config = Config::new();
    let socket_path = config.socket.to_string();
    let server = UnixSocketServer::new(socket_path);

    // Handle Ctrl-C gracefully
    tokio::select! {
        result = server.start() => {
            if let Err(e) = result {
                eprintln!("Server error: {}", e);
            }
        }
        _ = tokio::signal::ctrl_c() => {
            println!("Shutting down server...");
        }
    }

    Ok(())
}
