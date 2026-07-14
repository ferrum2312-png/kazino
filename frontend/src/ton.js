import { beginCell } from '@ton/core'

// Owner's TON wallet — all deposits are sent here.
export const TON_DEPOSIT_ADDRESS =
  'UQAyMFJX-kJF44Em2HVHq6gjTWKOIGXKTEDL6AMJ6JqNEfXA'

// Standard TON text-comment body cell (op=0 + text), as base64 BoC.
function commentPayload(text) {
  return beginCell()
    .storeUint(0, 32)
    .storeStringTail(text)
    .endCell()
    .toBoc()
    .toString('base64')
}

// Send `amountTon` GRAM to the owner address with a `dep:<userId>` comment so
// the backend watcher can attribute and credit the deposit. Requires a
// connected wallet (tonConnectUI). Resolves with { boc } on success.
export async function depositTon(tonConnectUI, amountTon, comment) {
  const nano = String(Math.round(Number(amountTon) * 1e9))
  const message = { address: TON_DEPOSIT_ADDRESS, amount: nano }
  if (comment) message.payload = commentPayload(comment)
  const tx = {
    validUntil: Math.floor(Date.now() / 1000) + 300,
    messages: [message],
  }
  return tonConnectUI.sendTransaction(tx)
}
