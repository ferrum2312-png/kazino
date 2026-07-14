// Must be imported FIRST (before any module that pulls in @ton/core).
// @ton/core expects Node's Buffer / global to exist.
import { Buffer } from 'buffer'

if (!globalThis.Buffer) globalThis.Buffer = Buffer
if (!globalThis.global) globalThis.global = globalThis
