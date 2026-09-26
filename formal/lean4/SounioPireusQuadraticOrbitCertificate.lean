/-
  Finite certificate for the admitted affine action on the 1024 quadratic codes.

  The sign is `SounioCDCocycle.cdSigma`. Ordered bases of F₂⁴ supply the 20160
  elements of GL(4,2). A basis-and-swap pair is admitted when the Cayley-Dickson
  delta lies in bilinear forms plus coboundaries. The theorem is one
  `native_decide` of that finite action. The same check compares all 1024 class
  ids with the table copied from `continuity/novelty_oracle.sio`. That binds the
  source literal, not the compiled ELF. `claimReady` stays false.
-/
import SounioCDCocycle

namespace SounioPireusQuadraticOrbitCertificate

set_option maxHeartbeats 0
set_option maxRecDepth 1000000

def bit (value coordinate : Nat) : Nat :=
  (value / 2 ^ coordinate) % 2

def parity4 (value : Nat) : Nat :=
  (bit value 0 + bit value 1 + bit value 2 + bit value 3) % 2

def row (code index : Nat) : Nat :=
  (code / 2 ^ (4 * index)) % 16

def applyCode (code vector : Nat) : Nat :=
  parity4 (row code 0 &&& vector)
    + parity4 (row code 1 &&& vector) * 2
    + parity4 (row code 2 &&& vector) * 4
    + parity4 (row code 3 &&& vector) * 8

def pack (r0 r1 r2 r3 : Nat) : Nat :=
  r0 + r1 * 16 + r2 * 256 + r3 * 4096

def cdBit (left right : Nat) : Nat :=
  if SounioCDCocycle.cdSigma left right 4 < 0 then 1 else 0

def delta (code : Nat) (swap : Bool) (left right : Nat) : Nat :=
  let imageLeft := applyCode code left
  let imageRight := applyCode code right
  let source := if swap then cdBit imageRight imageLeft else cdBit imageLeft imageRight
  source ^^^ cdBit left right

def reconstructed (code : Nat) (swap : Bool) (rowIndex column : Nat) : Nat :=
  if rowIndex == column then
    delta code swap (2 ^ rowIndex) (2 ^ rowIndex)
  else if rowIndex < column then
    delta code swap (2 ^ rowIndex ^^^ 2 ^ column) (2 ^ rowIndex ^^^ 2 ^ column)
      ^^^ delta code swap (2 ^ rowIndex) (2 ^ rowIndex)
      ^^^ delta code swap (2 ^ column) (2 ^ column)
  else
    0

def bilinear (code : Nat) (swap : Bool) (left right : Nat) : Nat :=
  (List.range 4).foldl (fun total rowIndex =>
    if bit left rowIndex == 0 then total else
      (List.range 4).foldl (fun inner column =>
        if bit right column == 0 then inner else
          inner ^^^ reconstructed code swap rowIndex column) total) 0

def remainder (code : Nat) (swap : Bool) (left right : Nat) : Nat :=
  delta code swap left right ^^^ bilinear code swap left right

def coboundaryValue (code : Nat) (swap : Bool) : Bool :=
  let q3 := remainder code swap 1 2
  let q5 := remainder code swap 1 4
  let q9 := remainder code swap 1 8
  let q6 := remainder code swap 2 4
  let q10 := remainder code swap 2 8
  let q12 := remainder code swap 4 8
  let q7 := remainder code swap 3 4 ^^^ q3
  let q11 := remainder code swap 3 8 ^^^ q3
  let q13 := remainder code swap 5 8 ^^^ q5
  let q14 := remainder code swap 6 8 ^^^ q6
  let q15 := remainder code swap 7 8 ^^^ q7
  let value index :=
    if index == 3 then q3 else if index == 5 then q5 else if index == 6 then q6
    else if index == 7 then q7 else if index == 9 then q9 else if index == 10 then q10
    else if index == 11 then q11 else if index == 12 then q12 else if index == 13 then q13
    else if index == 14 then q14 else if index == 15 then q15 else 0
  let diagonal :=
    (List.range 16).all fun index =>
      remainder code swap index 0 == 0
        && remainder code swap 0 index == 0
        && remainder code swap index index == 0
  diagonal && (List.range 16).all fun left =>
    (List.range 16).all fun right =>
      remainder code swap left right
        == (value left ^^^ value right ^^^ value (left ^^^ right))

def glCodes : List Nat :=
  (List.range 15).flatMap fun raw0 =>
    let r0 := raw0 + 1
    (List.range 15).flatMap fun raw1 =>
      let r1 := raw1 + 1
      if r1 == r0 then [] else
        (List.range 15).flatMap fun raw2 =>
          let r2 := raw2 + 1
          if r2 == r0 || r2 == r1 || r2 == (r0 ^^^ r1) then [] else
            (List.range 15).flatMap fun raw3 =>
              let r3 := raw3 + 1
              let span3 := [r0, r1, r0 ^^^ r1, r2, r0 ^^^ r2, r1 ^^^ r2, r0 ^^^ r1 ^^^ r2]
              if span3.contains r3 then [] else [pack r0 r1 r2 r3]

def admittedPairsFrom (codes : List Nat) : List (Nat × Bool) :=
  codes.flatMap fun code =>
    (if coboundaryValue code false then [(code, false)] else [])
      ++ (if coboundaryValue code true then [(code, true)] else [])

def evalQ (code vector : Nat) : Nat :=
  bit code 0 * bit vector 0 ^^^ bit code 1 * bit vector 1
    ^^^ bit code 2 * bit vector 2 ^^^ bit code 3 * bit vector 3
    ^^^ bit code 4 * bit vector 0 * bit vector 1
    ^^^ bit code 5 * bit vector 0 * bit vector 2
    ^^^ bit code 6 * bit vector 0 * bit vector 3
    ^^^ bit code 7 * bit vector 1 * bit vector 2
    ^^^ bit code 8 * bit vector 1 * bit vector 3
    ^^^ bit code 9 * bit vector 2 * bit vector 3

def codeOfDiagonal (entry : Nat → Nat) : Nat :=
  entry 1 + entry 2 * 2 + entry 4 * 4 + entry 8 * 8
    + (entry 3 ^^^ entry 1 ^^^ entry 2) * 16
    + (entry 5 ^^^ entry 1 ^^^ entry 4) * 32
    + (entry 9 ^^^ entry 1 ^^^ entry 8) * 64
    + (entry 6 ^^^ entry 2 ^^^ entry 4) * 128
    + (entry 10 ^^^ entry 2 ^^^ entry 8) * 256
    + (entry 12 ^^^ entry 4 ^^^ entry 8) * 512

def displacement (code : Nat) (swap : Bool) : Nat :=
  codeOfDiagonal (fun index => delta code swap index index)

def act (code : Nat) (swap : Bool) (quadratic : Nat) : Nat :=
  codeOfDiagonal (fun index => evalQ quadratic (applyCode code index))
    ^^^ displacement code swap

def getAt (parent : Array Nat) (index : Nat) : Nat :=
  parent[index]?.getD index

def setAt (parent : Array Nat) (index value : Nat) : Array Nat :=
  if h : index < parent.size then parent.set index value h else parent

def findRoot (fuel : Nat) (parent : Array Nat) (index : Nat) : Nat :=
  match fuel with
  | 0 => index
  | fuel + 1 =>
      let next := getAt parent index
      if next == index then index else findRoot fuel parent next

def unite (parent : Array Nat) (left right : Nat) : Array Nat :=
  let rootLeft := findRoot 1024 parent left
  let rootRight := findRoot 1024 parent right
  if rootLeft == rootRight then parent else setAt parent rootLeft rootRight

def orbitParentFrom (pairs : List (Nat × Bool)) : Array Nat :=
  pairs.foldl (fun parent action =>
    (List.range 1024).foldl (fun current quadratic =>
      unite current quadratic (act action.1 action.2 quadratic)) parent)
    ((List.range 1024).foldl (fun parent index => parent.push index) #[])

def rootIn (parent : Array Nat) (quadratic : Nat) : Nat :=
  findRoot 1024 parent quadratic

def classMinima (parent : Array Nat) : List Nat :=
  let roots := (List.range 1024).filter fun quadratic => rootIn parent quadratic == quadratic
  (roots.map fun root =>
    ((List.range 1024).filter fun quadratic => rootIn parent quadratic == root).foldl
      min root).mergeSort

def classSizes (parent : Array Nat) (minima : List Nat) : List Nat :=
  minima.map fun minimum =>
    ((List.range 1024).filter fun quadratic =>
      rootIn parent quadratic == rootIn parent minimum).length

def frozenMinima : List Nat :=
  [0, 1, 8, 9, 16, 19, 20, 24, 27, 28,
   64, 65, 66, 72, 73, 74, 80, 82, 83, 84,
   88, 90, 91, 92, 192, 193, 198, 199, 200, 201, 206, 207]

def embeddedSourceClasses : Array Nat := #[
    0, 1, 1, 1, 1, 1, 1, 1, 2, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 5, 6, 6, 6, 6, 7, 7, 7, 8, 9, 9, 9, 9,
    4, 4, 6, 6, 4, 5, 6, 6, 7, 7, 9, 9, 7, 8, 9, 9, 4, 4, 6, 6, 6, 6, 4, 5, 7, 7, 9, 9, 9, 9, 7, 8,
    10, 11, 12, 12, 12, 12, 12, 12, 13, 14, 15, 15, 15, 15, 15, 15, 16, 16, 17, 18, 19, 19, 19, 19, 20, 20, 21, 22, 23, 23, 23, 23,
    16, 16, 19, 19, 17, 18, 19, 19, 20, 20, 23, 23, 21, 22, 23, 23, 16, 16, 19, 19, 19, 19, 17, 18, 20, 20, 23, 23, 23, 23, 21, 22,
    4, 6, 4, 6, 4, 6, 5, 6, 7, 9, 7, 9, 7, 9, 8, 9, 4, 6, 4, 6, 6, 4, 6, 5, 7, 9, 7, 9, 9, 7, 9, 8,
    4, 6, 6, 4, 4, 6, 6, 5, 7, 9, 9, 7, 7, 9, 9, 8, 6, 4, 4, 6, 4, 6, 6, 5, 9, 7, 7, 9, 7, 9, 9, 8,
    24, 25, 24, 25, 24, 25, 26, 27, 28, 29, 28, 29, 28, 29, 30, 31, 24, 25, 24, 25, 25, 24, 27, 26, 28, 29, 28, 29, 29, 28, 31, 30,
    24, 25, 25, 24, 24, 25, 27, 26, 28, 29, 29, 28, 28, 29, 31, 30, 25, 24, 24, 25, 24, 25, 27, 26, 29, 28, 28, 29, 28, 29, 31, 30,
    10, 12, 11, 12, 12, 12, 12, 12, 13, 15, 14, 15, 15, 15, 15, 15, 16, 17, 16, 18, 19, 19, 19, 19, 20, 21, 20, 22, 23, 23, 23, 23,
    24, 24, 25, 25, 24, 26, 25, 27, 28, 28, 29, 29, 28, 30, 29, 31, 24, 24, 25, 25, 25, 27, 24, 26, 28, 28, 29, 29, 29, 31, 28, 30,
    10, 12, 12, 11, 12, 12, 12, 12, 13, 15, 15, 14, 15, 15, 15, 15, 17, 16, 16, 18, 19, 19, 19, 19, 21, 20, 20, 22, 23, 23, 23, 23,
    24, 24, 25, 25, 24, 26, 27, 25, 28, 28, 29, 29, 28, 30, 31, 29, 24, 24, 25, 25, 27, 25, 24, 26, 28, 28, 29, 29, 31, 29, 28, 30,
    16, 19, 16, 19, 17, 19, 18, 19, 20, 23, 20, 23, 21, 23, 22, 23, 16, 19, 16, 19, 19, 17, 19, 18, 20, 23, 20, 23, 23, 21, 23, 22,
    24, 25, 25, 24, 24, 27, 25, 26, 28, 29, 29, 28, 28, 31, 29, 30, 25, 24, 24, 25, 24, 27, 25, 26, 29, 28, 28, 29, 28, 31, 29, 30,
    24, 25, 24, 25, 24, 27, 26, 25, 28, 29, 28, 29, 28, 31, 30, 29, 24, 25, 24, 25, 27, 24, 25, 26, 28, 29, 28, 29, 31, 28, 29, 30,
    16, 19, 19, 16, 17, 19, 19, 18, 20, 23, 23, 20, 21, 23, 23, 22, 19, 16, 16, 19, 17, 19, 19, 18, 23, 20, 20, 23, 21, 23, 23, 22,
    10, 12, 12, 12, 11, 12, 12, 12, 13, 15, 15, 15, 14, 15, 15, 15, 24, 24, 24, 26, 25, 25, 25, 27, 28, 28, 28, 30, 29, 29, 29, 31,
    16, 17, 19, 19, 16, 18, 19, 19, 20, 21, 23, 23, 20, 22, 23, 23, 24, 24, 25, 27, 25, 25, 24, 26, 28, 28, 29, 31, 29, 29, 28, 30,
    10, 12, 12, 12, 12, 11, 12, 12, 13, 15, 15, 15, 15, 14, 15, 15, 24, 24, 24, 26, 25, 25, 27, 25, 28, 28, 28, 30, 29, 29, 31, 29,
    17, 16, 19, 19, 16, 18, 19, 19, 21, 20, 23, 23, 20, 22, 23, 23, 24, 24, 27, 25, 25, 25, 24, 26, 28, 28, 31, 29, 29, 29, 28, 30,
    16, 19, 17, 19, 16, 19, 18, 19, 20, 23, 21, 23, 20, 23, 22, 23, 24, 25, 24, 27, 25, 24, 25, 26, 28, 29, 28, 31, 29, 28, 29, 30,
    16, 19, 19, 17, 16, 19, 19, 18, 20, 23, 23, 21, 20, 23, 23, 22, 25, 24, 24, 27, 24, 25, 25, 26, 29, 28, 28, 31, 28, 29, 29, 30,
    24, 25, 24, 27, 24, 25, 26, 25, 28, 29, 28, 31, 28, 29, 30, 29, 16, 19, 17, 19, 19, 16, 19, 18, 20, 23, 21, 23, 23, 20, 23, 22,
    24, 25, 27, 24, 24, 25, 25, 26, 28, 29, 31, 28, 28, 29, 29, 30, 19, 16, 17, 19, 16, 19, 19, 18, 23, 20, 21, 23, 20, 23, 23, 22,
    10, 12, 12, 12, 12, 12, 11, 12, 13, 15, 15, 15, 15, 15, 14, 15, 24, 24, 24, 26, 25, 27, 25, 25, 28, 28, 28, 30, 29, 31, 29, 29,
    24, 24, 25, 27, 24, 26, 25, 25, 28, 28, 29, 31, 28, 30, 29, 29, 16, 17, 19, 19, 19, 19, 16, 18, 20, 21, 23, 23, 23, 23, 20, 22,
    10, 12, 12, 12, 12, 12, 12, 11, 13, 15, 15, 15, 15, 15, 15, 14, 24, 24, 24, 26, 27, 25, 25, 25, 28, 28, 28, 30, 31, 29, 29, 29,
    24, 24, 27, 25, 24, 26, 25, 25, 28, 28, 31, 29, 28, 30, 29, 29, 17, 16, 19, 19, 19, 19, 16, 18, 21, 20, 23, 23, 23, 23, 20, 22,
    17, 19, 16, 19, 16, 19, 18, 19, 21, 23, 20, 23, 20, 23, 22, 23, 24, 27, 24, 25, 25, 24, 25, 26, 28, 31, 28, 29, 29, 28, 29, 30,
    24, 27, 25, 24, 24, 25, 25, 26, 28, 31, 29, 28, 28, 29, 29, 30, 19, 17, 16, 19, 16, 19, 19, 18, 23, 21, 20, 23, 20, 23, 23, 22,
    24, 27, 24, 25, 24, 25, 26, 25, 28, 31, 28, 29, 28, 29, 30, 29, 17, 19, 16, 19, 19, 16, 19, 18, 21, 23, 20, 23, 23, 20, 23, 22,
    17, 19, 19, 16, 16, 19, 19, 18, 21, 23, 23, 20, 20, 23, 23, 22, 27, 24, 24, 25, 24, 25, 25, 26, 31, 28, 28, 29, 28, 29, 29, 30,
  ]

def frozenSizes : List Nat :=
  [1, 7, 1, 7, 21, 7, 28, 21, 7, 28,
   7, 7, 42, 7, 7, 42, 42, 21, 21, 84,
   42, 21, 21, 84, 84, 84, 28, 28, 84, 84, 28, 28]

def classIndex (minima : List Nat) (parent : Array Nat) (quadratic : Nat) : Nat :=
  let root := rootIn parent quadratic
  minima.findIdx fun minimum => rootIn parent minimum == root

def certificate : Bool :=
  let codes := glCodes
  let admitted := admittedPairsFrom codes
  let parent := orbitParentFrom admitted
  let minima := classMinima parent
  let sizes := classSizes parent minima
  let bound := (List.range 1024).all fun code =>
    embeddedSourceClasses[code]? == some (classIndex minima parent code)
  codes.length == 20160
    && codes.eraseDups.length == 20160
    && admitted.length == 336
    && minima == frozenMinima
    && sizes == frozenSizes
    && sizes.foldl (· + ·) 0 == 1024
    && embeddedSourceClasses.size == 1024
    && bound

theorem quadratic_orbit_certificate : certificate = true := by
  native_decide

structure Boundary where
  certificateProved : Bool
  sourceTableBindingProved : Bool
  semanticBindingProved : Bool
  byteBindingProved : Bool
  claimReady : Bool
deriving DecidableEq, Repr

def boundary : Boundary :=
  { certificateProved := true
  , sourceTableBindingProved := true
  , semanticBindingProved := true
  , byteBindingProved := false
  , claimReady := false }

theorem quadratic_orbit_certificate_does_not_promote_a_claim :
    boundary.certificateProved = true
      && boundary.sourceTableBindingProved = true
      && boundary.semanticBindingProved = true
      && boundary.byteBindingProved = false
      && boundary.claimReady = false := by
  decide

end SounioPireusQuadraticOrbitCertificate
