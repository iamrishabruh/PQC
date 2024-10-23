# BB84 Protocol Example DSL Script
qubit q0
qubit q1
qubit q2

alice_send q0
alice_send q1
alice_send q2

bob_measure q0 H
bob_measure q1 X
bob_measure q2 H

sift_keys
check_eavesdropping
generate_key k0
print k0
