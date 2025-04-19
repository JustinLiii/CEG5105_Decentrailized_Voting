const crypto = require("crypto");

/**
 * RSA Blind Signature Implementation in JavaScript (Node.js)
 *
 * Provides functions to blind a message, sign the blinded message,
 * unblind the signature, and verify signatures using BigInt.
 */

/**
 * Generate a random BigInt in range [2, max-1], uniformly.
 * Uses Node.js crypto.randomBytes.
 * @param {BigInt} max - upper bound (exclusive)
 * @returns {BigInt}
 */
function randomBigInt(max) {
  const bitLength = max.toString(2).length;
  const byteLength = Math.ceil(bitLength / 8);
  let rand;
  do {
    const buf = crypto.randomBytes(byteLength);
    rand = BigInt('0x' + buf.toString('hex'));
  } while (rand < 2n || rand >= max);
  return rand;
}

/**
 * Compute modular exponentiation: base^exp mod mod.
 * @param {BigInt} base
 * @param {BigInt} exp
 * @param {BigInt} mod
 * @returns {BigInt}
 */
function modPow(base, exp, mod) {
  let result = 1n;
  let b = base % mod;
  let e = exp;
  while (e > 0) {
    if (e & 1n) result = (result * b) % mod;
    b = (b * b) % mod;
    e >>= 1n;
  }
  return result;
}

/**
 * Compute GCD of two BigInts.
 * @param {BigInt} a
 * @param {BigInt} b
 * @returns {BigInt}
 */
function gcd(a, b) {
  let x = a < 0n ? -a : a;
  let y = b < 0n ? -b : b;
  while (y) {
    [x, y] = [y, x % y];
  }
  return x;
}

/**
 * Extended Euclidean algorithm.
 * Returns [g, x, y] such that ax + by = g = gcd(a, b).
 * @param {BigInt} a
 * @param {BigInt} b
 * @returns {[BigInt, BigInt, BigInt]}
 */
function extendedGcd(a, b) {
  let old_r = a;
  let r = b;
  let old_s = 1n;
  let s = 0n;
  let old_t = 0n;
  let t = 1n;

  while (r !== 0n) {
    const q = old_r / r;
    [old_r, r] = [r, old_r - q * r];
    [old_s, s] = [s, old_s - q * s];
    [old_t, t] = [t, old_t - q * t];
  }

  return [old_r, old_s, old_t];
}

/**
 * Compute modular inverse of a mod m.
 * @param {BigInt} a
 * @param {BigInt} m
 * @returns {BigInt}
 * @throws {Error} if inverse does not exist
 */
function modInv(a, m) {
  const [g, x] = extendedGcd(a, m);
  if (g !== 1n) throw new Error('Modular inverse does not exist');
  return (x % m + m) % m;
}

/**
 * Public RSA parameters.
 * @typedef {Object} RSAPublicKey
 * @property {BigInt} n - modulus
 * @property {BigInt} e - public exponent
 */

/**
 * Private RSA parameters.
 * @typedef {Object} RSAPrivateKey
 * @property {BigInt} p - prime1
 * @property {BigInt} q - prime2
 * @property {BigInt} d - private exponent
 * @property {BigInt} n - modulus (p*q)
 */

/**
 * Blind a message.
 * @param {RSAPublicKey} pub
 * @param {BigInt} message
 * @returns {{blinded: BigInt, r: BigInt}}
 */
export function blind(pub, message) {
  const { n, e } = pub;
  let r;
  do {
    r = randomBigInt(n);
  } while (gcd(r, n) !== 1n);

  const blinded = (message * modPow(r, e, n)) % n;
  return { blinded, r };
}

/**
 * Sign a blinded message.
 * @param {RSAPrivateKey} priv
 * @param {BigInt} blinded
 * @returns {BigInt}
 */
export function sign(priv, blinded) {
  return modPow(blinded, priv.d, priv.n);
}

/**
 * Unblind a signature.
 * @param {RSAPublicKey} pub
 * @param {BigInt} blindedSig
 * @param {BigInt} r
 * @returns {BigInt}
 */
export function unblind(pub, blindedSig, r) {
  const rInv = modInv(r, pub.n);
  return (blindedSig * rInv) % pub.n;
}

/**
 * Verify a signature on a message.
 * @param {RSAPublicKey} pub
 * @param {BigInt} message
 * @param {BigInt} signature
 * @returns {boolean}
 */
export function verify(pub, message, signature) {
  return modPow(signature, pub.e, pub.n) === message;
}
