#init 
MW102 = 66
MW124 = 0
MW110 = 0
MW150 = 0
MW120 = 0
MW126 = 0
MW128 = 0
MW180 = 0
MW190 = 0
MW200 = 0

def scan() :
  global MW102,MW124,MW110,MW150,MW120,MW126,MW128,MW180,MW190,MW200
  
  MW102 = 66
  MW102 = MW102 + 3
  MW110 = MW102 << 2
  MW150 = MW110 / 2
  MW150 = MW150 * 2
  MW120 = MW150 / 2
  if MW124 < MW120 :
     MW124 = MW124 + 1
  MW126 = MW124 * 8
  MW128 = MW126 >> 3
  if MW124 == 88 :
     MW180 = MW124 * 88
  else:
     MW180 = MW124 + 88
  MW190 = MW124 + 88
  MW190 = MW190 * 2
  MW200 = MW190 - 88
  if MW180 > MW190 :
     MW200 = MW180 / 88
  elif MW180 == MW190 :
     MW200 = MW180 - 4
  else:
     MW200 = MW190 - MW180

cycle_n = 0
l1_MW200 = -1
l2_MW200 = -2
while l1_MW200 != l2_MW200 :
  scan()
  l1_MW200 = l2_MW200
  l2_MW200 = MW200
  cycle_n = cycle_n + 1	

print("scan cycle %d MW200 %d\n" % (cycle_n,MW200))

