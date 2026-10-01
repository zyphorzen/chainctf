# ChainCTF Threat Model

## Assets

- Player wallet
- Challenge metadata
- Challenge flags
- Player score
- Achievement state
- Verifier private key

## Attacker Capabilities

An attacker may:

- Read all blockchain data
- Inspect smart contract code
- Call public/external functions
- Modify frontend code
- Call backend APIs directly
- Submit invalid proofs
- Replay transactions
- Create multiple wallets

## Trust Boundaries

### Frontend

Untrusted.

### Backend

Trusted for challenge verification.

### Smart Contract

Trusted for immutable state transitions.

### Blockchain

Trusted for transaction execution and consensus.

## Security Requirements

1. Only owner can create challenges.
2. Only owner can change challenge state.
3. A player can solve a challenge only once.
4. Score cannot be increased without a valid achievement authorization.
5. Authorization must expire.
6. Authorization must not be replayable.
7. Verifier private key must never be exposed.
8. Challenge flags must never be stored on-chain.
9. Frontend must not be trusted for authorization.
10. Sensitive secrets must never be committed to Git.

## Future Improvements

- EIP-712 typed signatures
- Signature-based authorization
- Nonce management
- Deadline validation
- Rate limiting
- Sybil resistance
- Zero-knowledge proof research