use std::io::{BufRead, BufReader};
use std::process::{Command, Stdio};

#[tauri::command]
async fn run_script(path: String, quality: u32, lossless: bool, app: tauri::AppHandle) -> Result<(), String> {
    let mut cmd = Command::new("sh");
    cmd.arg("src-tauri/resources/seo_image_processor.sh");
    cmd.arg(&path);
    if lossless {
        cmd.arg("--lossless");
    } else {
        cmd.arg("--quality");
        cmd.arg(quality.to_string());
    }
    let mut child = cmd.stdout(Stdio::piped()).stderr(Stdio::piped()).spawn().map_err(|e| e.to_string())?;

    let stdout = child.stdout.take().unwrap();
    let stderr = child.stderr.take().unwrap();

    let app_clone = app.clone();
    tauri::async_runtime::spawn(async move {
        let reader = BufReader::new(stdout);
        for line in reader.lines() {
            if let Ok(line) = line {
                app_clone.emit_all("log", line).unwrap();
            }
        }
    });

    let app_clone = app.clone();
    tauri::async_runtime::spawn(async move {
        let reader = BufReader::new(stderr);
        for line in reader.lines() {
            if let Ok(line) = line {
                app_clone.emit_all("log", format!("ERROR: {}", line)).unwrap();
            }
        }
    });

    child.wait().map_err(|e| e.to_string())?;
    Ok(())
}

pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![run_script])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
