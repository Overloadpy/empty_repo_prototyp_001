use std::env;

fn main() {
    // Tell Cargo that if the given file changes, to rerun this build script
    println!("cargo:rerun-if-changed=src/lib.rs");
    
    // Get the target OS
    let target_os = env::var("CARGO_CFG_TARGET_OS").unwrap_or_default();
    
    // Set up platform-specific configurations
    match target_os.as_str() {
        "android" => {
            // Android-specific build configurations
            println!("cargo:rustc-link-lib=flutter_rust_bridge");
        }
        "ios" => {
            // iOS-specific build configurations
            println!("cargo:rustc-link-lib=flutter_rust_bridge");
        }
        "linux" => {
            // Linux-specific build configurations
            println!("cargo:rustc-link-lib=flutter_rust_bridge");
        }
        "macos" => {
            // macOS-specific build configurations
            println!("cargo:rustc-link-lib=flutter_rust_bridge");
        }
        "windows" => {
            // Windows-specific build configurations
            println!("cargo:rustc-link-lib=flutter_rust_bridge");
        }
        _ => {
            // Default case
        }
    }
}