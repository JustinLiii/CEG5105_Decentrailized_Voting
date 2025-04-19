const { blind, unblind, verify } = require('./blind_sign.js');
/**
 * Fetches and parses a PEM-encoded SPKI public key into ArrayBuffer
 * @param {string} pem - PEM string
 * @returns {ArrayBuffer}
 */
function pemToArrayBuffer(pem) {
    // Remove PEM header/footer and newlines
    const b64 = pem.replace(/-----BEGIN PUBLIC KEY-----|-----END PUBLIC KEY-----|\s+/g, '');
    const binary = window.atob(b64);
    const len = binary.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  }
  
  /**
   * Convert a base64url string to a Uint8Array
   * @param {string} base64url
   */
  function base64urlToUint8Array(base64url) {
    const b64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
    const pad = b64.length % 4;
    const padded = b64 + (pad ? '='.repeat(4 - pad) : '');
    const str = window.atob(padded);
    const arr = new Uint8Array(str.length);
    for (let i = 0; i < str.length; i++) {
      arr[i] = str.charCodeAt(i);
    }
    return arr;
  }
  
  /**
   * Convert a Uint8Array to a hex string
   * @param {Uint8Array} bytes
   */
  function uint8ArrayToHex(bytes) {
    return Array.from(bytes)
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }
  
  /**
   * Convert base64url JWK value to hex for BigInt parsing
   * @param {string} b64url
   */
  function base64urlToHex(b64url) {
    const bytes = base64urlToUint8Array(b64url);
    return uint8ArrayToHex(bytes);
  }
  
  /**
   * Performs the blind-sign request flow in the browser.
   * @param {string} userName
   * @param {string} userId
   * @param {string} serverUrl
   * @returns {Promise<string>} - Assigned anonymous account address
   */
  export async function blindSignRequest(userName, userId, serverUrl) {
    // Step 1: Fetch and load public key
    const pemText = await fetch(`${serverUrl}/public.pem`).then(r => {
      if (!r.ok) throw new Error(`Failed to fetch public key: ${r.statusText}`);
      return r.text();
    });
  
    const spkiBuffer = pemToArrayBuffer(pemText);
    // Import SPKI key and export to JWK to obtain n and e
    const cryptoKey = await window.crypto.subtle.importKey(
      'spki',
      spkiBuffer,
      { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' },
      true,
      []
    );
    const jwk = await window.crypto.subtle.exportKey('jwk', cryptoKey);
    const n = BigInt('0x' + base64urlToHex(jwk.n));
    const e = BigInt('0x' + base64urlToHex(jwk.e));
  
    const pub = { n, e };
  
    // Step 2: Hash user info
    const userInfo = { voter_id: userId, voter_name: userName };
    const sortedKeys = Object.keys(userInfo).sort();
    const payload = sortedKeys.reduce((obj, key) => {
      obj[key] = userInfo[key];
      return obj;
    }, {});
    const jsonStr = JSON.stringify(payload);
    const encoder = new TextEncoder();
    const data = encoder.encode(jsonStr);
    const hashBuffer = await window.crypto.subtle.digest('SHA-256', data);
    const hashArray = new Uint8Array(hashBuffer);
    const hashHex = Array.from(hashArray).map(b => b.toString(16).padStart(2, '0')).join('');
    const message = BigInt('0x' + hashHex);
  
    // Step 3: Blind the message
    const { blinded, r } = blind(pub, message);
  
    // Step 4: Request blind signature from server
    const blindResp = await fetch(`${serverUrl}/blind_sign`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ blinded_message: blinded.toString() })
    });
    if (!blindResp.ok) throw new Error(`Blind sign request failed: ${blindResp.statusText}`);
    const blindData = await blindResp.json();
    const blindedSignature = BigInt(blindData.blind_signature);
  
    // Step 5: Unblind the signature
    const signature = unblind(pub, blindedSignature, r);
  
    // Step 6: Verify signature
    if (!verify(pub, message, signature)) {
      throw new Error('Signature verification failed!');
    }
  
    // Step 7: Request account assignment
    const assignResp = await fetch(`${serverUrl}/assign_account`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json'},
      body: JSON.stringify({ user_hash: message.toString(), signature: signature.toString() })
    });
    if (!assignResp.ok) {
      const text = await assignResp.text();
      throw new Error(`Account assignment failed: ${assignResp.status} ${text}`);
    }
    const assignData = await assignResp.json();
    const accountAddress = assignData.account_address;
  
    console.log(`Successfully obtained anonymous account: ${accountAddress}`);
    return accountAddress;
  }

// get user info
export function getUserInfo() {

  const voterName = localStorage.getItem('voter_name');
  const voterId = localStorage.getItem('voter_id');

  if (!voterName || !voterId) {
    console.error("User info not found in session storage");
    return null;
  }
  return { voterName, voterId };
}