# Slip Kiosk - exe repo (loader only)

Is repo mein app ka code nahi hai. exe start hote hi `loader.py` mein likhe Pages link se
`slip_bridge.py` aur `slip_kiosk_app.py` download karta hai aur chalata hai.

1. `loader.py` mein `CODE_URL` par code repo ka Pages link daalein.
2. Actions > Run workflow > exe download karein (Artifacts > SlipKiosk).
3. Code badalna ho to sirf code repo mein edit karein - exe dobara banane ki zaroorat nahi
   (naya code exe agli dafa start hone par aata hai).

exe dobara tab banana hai jab app mein koi **nayi library** lagani ho.
