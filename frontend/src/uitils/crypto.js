const encoder = new TextEncoder();

export async function sha256(message) {
    let bytes = await crypto.subtle.digest("SHA-256", encoder.encode(message));
    let a = Array.from(new Uint8Array(bytes)); // convert buffer to byte array
    let hex = a
        .map((b) => b.toString(16).padStart(2, "0"))
        .join(""); // convert bytes to hex string
    return hex;
}