# Hollow Reserve — HI Cyber Con 2026 — RESUELTO ✅

Flag: `hiCTF{th1n_p00l_was_the_r3al_0racle}` (63 pts)
Fecha: 2026-11-01 · Agente E5 · Equipo CROX Sec

## TL;DR del exploit
Flash-loan de 5e24 RSV del lender ERC-3156 → comprar COL en el mini-AMM interno
(precio spot = RSV_res*1e18/COL_res sube de 100 a ~2.6e23) → depositar ~980 COL
en CreditFacility (oracle = market.spotPrice, LTV 75%) → pedir prestado 9.5e24 RSV
del Vault (vacía 1e25 → 5e23 < initialReserve/10 = 1e24) → devolver 5e24 al lender.
Beneficio: 4.5e24 RSV. isSolved → GET /flag.

## Arquitectura (reversa desde bytecode, reto sin fuentes)
Cada instancia = anvil chainId 31337 con contratos deployados por un Setup.
Setup expone getters por slot: 741bef1a=feed, fbfa77cf=vault, 2eb02837=market,
a7714458=lender, a78695b0=COL, 4edd8b41=facility, fa715e38=CFA, ca38936e=RSV,
48db5f89=player, 64d98f6e=isSolved().

| Contrato | Selector principal | Lógica |
|---|---|---|
| Vault | lend(to,amt)=0xa2fb342d | solo facility (slot0); transfer RSV |
| RSV/COL | ERC20 estándar | 18 dec; supply RSV 2.51e25, COL ~2.5e21 |
| PriceFeed | getPrice()=0x98d5fdca | delega a market.spotPrice() |
| FlashLender | flashLoan=0x5cffe9de | ERC-3156; fee 0; PULL repayment via transferFrom (el receiver debe approve); magic onFlashLoan = 0x439148f0…cf18dd9 |
| Market (AMM) | **buy COL = 0x40f788d2(uint256 rsvIn, uint256 minColOut)** | UniswapV2 mini, reserves packed en slot0 (high112=RSV, low112=COL), fee 997/1000, spotPrice()=0x398482d8 = RSV*1e18/COL |
| Market | sell COL = 0xdce0772c(colIn, minRsvOut) | a la inversa |
| Market | RSV res = 0x360dc2c8 / COL res = 0xd79a6512 / packed = ? init=0xa5843f08(uint256,uint256) | init deposita liquidez inicial y setea flag "locked" |
| CreditFacility | **borrow(collateral, amount) = 0x0ecbcdab** | COL.transferFrom(caller); price=feed.getPrice(); require(amount ≤ collateral*price/1e18*7500/10000); collateralOf/debtOf+=; vault.lend(caller, amount) |
| CreditFacility | repay(amount)=0x371fd8e6 | proporcional: devuelve collateral*amount/debt |
| CreditFacility | collateralOf=0x1aefb107, debtOf=0xd283e75f, feed=0x37a7b7d8, vault=0xfbfa77cf | getters de mappings |

## Constantes del Setup (deterministas entre instancias)
initialReserve=1e25 · vault seed=1e25 · flashLender seed=5e24 (bb06aee9) ·
market seed: 1e23 RSV + 1e21 COL (4f043cc5/5ba135e5, f17f3963=100000e18?) ·
player: 1000 RSV + 100 COL · LTV=7500 (407c496d) · 500=f1128faf.

## La vulnerabilidad
El CreditFacility valora el colateral COL con market.spotPrice() INSTANTÁNEO
(reservas del AMM, sin TWAP ni flash-loan protection). El AMM tiene fee 0.3%
y liquidity boots 100k RSV/1k COL, pero el FlashLender presta 5e24 RSV gratis —
50x la reserva RSV del pool. Comprar COL con todo el loan vacía el pool de COL
y multiplica el spot por ~2.6 millones. Con 980 COL de colateral se puede pedir
prestado todo el Vault (1e25) 18 veces sobre. La condición isSolved solo mira
balanceOf(vault) < initialReserve/10; la deuda incobrable del facility da igual.

## Pasos exactos de explotación
1. `PUT /api/v2/integrations/challs/{id}/instance {}` → instancia (~19 min vida).
2. `GET {rpc}/info` → player key + setup address.
3. `cast call $SETUP <selector getter>` para sacar las 7 direcciones.
4. Deploy `HollowExploit.sol` (en /tmp/hollow/exploit/src/) con forge create --broadcast.
5. `attack(rsv, col, lend, market, facility, 5e24, 9.5e24)`:
   - flashLoan(this, rsv, 5e24, "")
   - onFlashLoan: approve(market, 5e24) → market.call(0x40f788d2, 5e24, 1)
     → colBal=balanceOf(this) → approve(facility, colBal) →
     facility.borrow(colBal, 9.5e24) → approve(lend, 5e24) → return MAGIC
6. Verificar: `cast call $SETUP 0x64d98f6e` == 1 → `GET {rpc}/flag`.
7. `POST /api/v1/challs/{id}/submit {"flag":"..."}`.

## TRAMPA CLAVE — selectores con nombre desconocido
Los contratos del reto NO usan nombres estándar. `cast sig` miente si adivinas mal:
- `swap(uint256,uint256)` = 0xd96073cf ≠ 0x40f788d2 → **revert vacío en fallback**.
- El buy del market es 0x40f788d2 (nombre real desconocido: posibles "buyCol" etc.)
- sell = 0xdce0772c. borrow SÍ es borrow(uint256,uint256)=0x0ecbcdab ✓.
- flashLoan(address,address,uint256,bytes)=0x5cffe9de ✓ estándar.
Regla: cuando el bytecode es la única fuente, llama con selector RAW
(`cast send $MKT 0x40f788d2$(python3 -c 'print(f"{a:064x}{b:064x}")')` o
`abi.encodeWithSelector(0x40f788d2, ...)` en Solidity). Revert con data "0x" =
selector no encontrado (fallback), no requiere con mensaje.

## Notas técnicas
- La instancia expira a los ~19 min (timeLeftMilliseconds). DELETE + PUT reinicia
  con direcciones NUEVAS pero mismo bytecode y mismas constantes.
- cast disassemble + grep de PUSH4 0x… para mapear el dispatcher; los getters
  del Setup te dan todas las direcciones sin leer storage a mano.
- El lender hace transferFrom(receiver, lender, amount+fee) DESPUÉS del callback:
  el contrato atacante DEBE approve(lender, amount+fee) antes de retornar el magic.
- fee = 0 (flashFee devuelve 0), así que basta devolver exactamente el loan.
- Maths del pool (UniswapV2): out = in*997*resOut / (resIn*1000 + in*997).
  Con 5e24 in: out ≈ 9.803e20 COL; res quedan RSV=5.11e24, COL=1.967e19;
  price ≈ 2.6e23 RSV/COL → maxBorrow con 980 COL ≈ 1.9e26 (vault solo tiene 1e25).
- Vault post-ataque: 5e23 < 1e24 → isSolved=true.

## Archivos
- Exploit: /tmp/hollow/exploit/src/HollowExploit.sol (compilado con solc 0.8.24)
- Disassemblies: /tmp/hollow/{setup,vault,feed,lend,cfa,c2e,c4e,res,col}.asm
- Challenge ID: bb99717c-d62a-4b9f-b0a4-017e257d8765
