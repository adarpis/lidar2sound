# OSC listener

live_loop :foo do
  use_real_time
  al, bl, cl, dl, el, fl, gl, gr, fr, er, dr, cr, br, ar, = sync "/osc/trigger/prophet"
  play :A, amp: al, pan: 1
  play :B, amp: bl, pan: 1
  play :C, amp: cl, pan: 1
  play :D, amp: dl, pan: 1
  play :E, amp: el, pan: 1
  play :F, amp: fl, pan: 1
  play :G, amp: gl, pan: 1
  play :A, amp: ar, pan: -1
  play :B, amp: br, pan: -1
  play :C, amp: cr, pan: -1
  play :D, amp: dr, pan: -1
  play :E, amp: er, pan: -1
  play :F, amp: fr, pan: -1
  play :G, amp: gr, pan: -1
end