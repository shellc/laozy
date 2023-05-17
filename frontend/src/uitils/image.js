export function encode_base64(data) {
    let bin = '';
    let bytes = new Uint8Array(data);
    for (let i = 0; i < bytes.byteLength; i++) {
        bin += String.fromCharCode(bytes[i])
    }
    let b64 = window.btoa(bin);
    return b64;
}