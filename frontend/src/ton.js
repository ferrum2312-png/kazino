// Owner's TON wallet — all deposits are sent here.
export const TON_DEPOSIT_ADDRESS =
  'UQAyMFJX-kJF44Em2HVHq6gjTWKOIGXKTEDL6AMJ6JqNEfXA'

// Send `amountTon` TON from the connected wallet to the owner address.
// Requires a connected wallet (tonConnectUI). Resolves with { boc } on success.
export async function depositTon(tonConnectUI, amountTon) {
  const nano = String(Math.round(Number(amountTon) * 1e9))
  const tx = {
    validUntil: Math.floor(Date.now() / 1000) + 300,
    messages: [{ address: TON_DEPOSIT_ADDRESS, amount: nano }],
  }
  return tonConnectUI.sendTransaction(tx)
}
