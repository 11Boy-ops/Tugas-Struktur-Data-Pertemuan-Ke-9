# 🔗 Advanced Linked Lists — Pertemuan 9

> Implementasi lengkap struktur data berbasis Linked List dalam Python, mencakup Doubly Linked List, Circular Linked List, Multi-Linked List, dan aplikasi nyata Text Editor Buffer.

---

## 📋 Daftar Isi

- [Gambaran Umum](#-gambaran-umum)
- [Doubly Linked List](#-doubly-linked-list)
- [Circular Linked List](#-circular-linked-list)
- [Multi-Linked List](#-multi-linked-list)
- [Complex Iterators](#-complex-iterators)
- [Aplikasi: Text Editor Buffer](#-aplikasi-text-editor-buffer)
- [Latihan Slide 39: Note-Taking App](#-latihan-slide-39-note-taking-app)
- [Perbandingan Kompleksitas](#-perbandingan-kompleksitas)
- [Cara Menjalankan](#-cara-menjalankan)

---

## 🌐 Gambaran Umum

Singly Linked List memiliki keterbatasan mendasar: traversal hanya satu arah, dan untuk mengakses node sebelumnya kita harus mulai dari head. Chapter ini memperkenalkan variasi-variasi yang mengatasi keterbatasan tersebut.

```
Singly:    HEAD → [A] → [B] → [C] → NULL

Doubly:    HEAD ⇄ [A] ⇄ [B] ⇄ [C] ⇄ TAIL

Circular:  listRef → [A] → [B] → [C] → (kembali ke A)

Multi:     headById  → [A] → [C] → [B]   (sorted by ID)
           headByName→ [A] → [B] → [C]   (sorted by Name)
           (node fisik sama, link berbeda)
```

---

## 🔗 Doubly Linked List

### Struktur Node

Setiap node memiliki **tiga field**: data, pointer ke node berikutnya (`.next`), dan pointer ke node sebelumnya (`.prev`).

```python
class DListNode:
    def __init__(self, data):
        self.data = data
        self.next = None   # → node berikutnya
        self.prev = None   # ← node sebelumnya
```

Diagram struktur:

```
NULL ← [prev|21|next] ⇄ [prev|37|next] ⇄ [prev|58|next] ⇄ [prev|74|next] → NULL
        ↑ HEAD                                                     ↑ TAIL
```

### Operasi Utama

#### Traversal Forward & Reverse

```python
def forwardTraversal(head):
    curNode = head
    while curNode is not None:
        print(curNode.data)
        curNode = curNode.next         # O(n)

def revTraversal(tail):
    curNode = tail
    while curNode is not None:
        print(curNode.data)
        curNode = curNode.prev         # O(n) — keunggulan DLL!
```

> **Keunggulan vs Singly:** Reverse traversal pada singly LL membutuhkan O(n²) atau rekursi/stack. DLL melakukannya dalam O(n) langsung via `.prev`.

#### Pencarian dengan Probe Technique

```python
# probe = referensi persisten antar operasi search
if target < probe.data:
    # Traverse mundur via .prev
    while probe is not None and target <= probe.data:
        if target == probe.data: return True
        probe = probe.prev
else:
    # Traverse maju via .next
    while probe is not None and target >= probe.data:
        if target == probe.data: return True
        probe = probe.next
return False
```

#### Insertion (4 Kasus)

```python
newnode = DListNode(value)

if head is None:                        # Kasus 1: List kosong
    head = tail = newnode

elif value < head.data:                 # Kasus 2: Insert di depan
    newnode.next = head
    head.prev = newnode
    head = newnode

elif value > tail.data:                 # Kasus 3: Insert di belakang
    newnode.prev = tail
    tail.next = newnode
    tail = newnode

else:                                   # Kasus 4: Insert di tengah
    node = head
    while node is not None and node.data < value:
        node = node.next
    newnode.next = node
    newnode.prev = node.prev
    node.prev.next = newnode
    node.prev = newnode
```

#### Deletion

```python
# Tidak perlu tracking predecessor — akses langsung via .prev
def delete_node(node, head, tail):
    if node.prev:
        node.prev.next = node.next     # Bypass dari kiri
    else:
        head = node.next               # Node adalah head baru

    if node.next:
        node.next.prev = node.prev     # Bypass dari kanan
    else:
        tail = node.prev               # Node adalah tail baru
```

### Analisis Kompleksitas

| Operasi | Waktu | Catatan |
|---------|-------|---------|
| Traversal (fwd/rev) | O(n) | Linear |
| Search tanpa probe | O(n) | Linear |
| Search dengan probe | O(n) worst, O(k) avg | k = jarak dari probe |
| Insert (sorted) | O(n) | Cari posisi |
| Insert (depan/belakang) | O(1) | Dengan referensi head/tail |
| Delete (ada referensi) | O(1) | Langsung via `.prev`/`.next` |

### Aplikasi Nyata

- **Browser History** — navigasi maju/mundur
- **Music Playlist** — next/previous track
- **Undo/Redo** — state traversal dua arah
- **LRU Cache** — eviction & access tracking

---

## 🔄 Circular Linked List

### Konsep

Node terakhir tidak menunjuk ke NULL, melainkan **kembali ke node pertama**, membentuk lingkaran.

```
listRef (menunjuk ke node TERAKHIR)
    ↓
[B] → [G] → [T] → [V]
 ↑________________________|
```

### Traversal (menggunakan flag `done`)

```python
def traverse(listRef):
    curNode = listRef
    done = (listRef is None)          # List kosong? Langsung selesai
    while not done:
        curNode = curNode.next        # Maju dulu, baru visit
        print(curNode.data)
        done = (curNode is listRef)   # Sudah balik ke awal?
```

> **Mengapa tidak pakai `while curNode is not None`?** Karena di circular list tidak ada NULL! Kita gunakan alias check (`curNode is listRef`) sebagai penanda akhir.

### Pencarian

```python
def searchCircular(listRef, target):
    curNode = listRef
    done = (listRef is None)
    while not done:
        curNode = curNode.next
        if curNode.data == target:
            return True
        done = (curNode is listRef) or (curNode.data > target)
    return False
```

### Insertion (4 Kasus)

```python
newNode = ListNode(value)

if listRef is None:                          # List kosong
    listRef = newNode
    newNode.next = newNode                   # Self-loop!

elif value < listRef.next.data:              # Insert di depan
    newNode.next = listRef.next
    listRef.next = newNode

elif value > listRef.data:                   # Insert di belakang
    newNode.next = listRef.next
    listRef.next = newNode
    listRef = newNode                        # Update listRef!

else:                                        # Insert di tengah
    predNode, curNode = None, listRef
    done = False
    while not done:
        predNode = curNode
        curNode = curNode.next
        done = (curNode is listRef) or (curNode.data > value)
    newNode.next = curNode
    predNode.next = newNode
```

### Aplikasi Nyata

- **CPU Scheduling** — round-robin process scheduling
- **Token Ring Network** — giliran kirim data
- **Media Player** — repeat playlist
- **Circular Buffer** — buffer dengan ukuran tetap

---

## 🔀 Multi-Linked List

### Konsep

Satu node memiliki **multiple link fields**, membentuk beberapa chain berbeda dalam koleksi node yang sama.

```
listByName ----→ [Smith,John] ---→ [Smith,Jane] ---→ NULL
                       |                  |
listById   ----→ [10015] ------→ [10142] -→ [10175] -→ [10210] → NULL
```

Node fisiknya **sama**, hanya diakses melalui pointer berbeda!

### Struktur Node

```python
class StudentMListNode:
    def __init__(self, data):
        self.data = data
        self.nextById   = None   # chain sorted by ID
        self.nextByName = None   # chain sorted by Name
```

### Sparse Matrix dengan Multi-Linked List

Matriks besar yang sebagian besar elemennya nol disimpan efisien dengan hanya menyimpan elemen non-zero:

```python
class MatrixMListNode:
    def __init__(self, row, col, value):
        self.row = row
        self.col = col
        self.value = value
        self.nextRow = None    # elemen berikutnya di baris yang sama
        self.nextCol = None    # elemen berikutnya di kolom yang sama
```

```
listOfRows[0] → (0,1,3) → (0,4,8) → NULL
listOfRows[1] → (1,0,2) → (1,3,1) → (1,6,5) → NULL
listOfCols[1] → (0,1,3) → (1,0,2) → (3,1,7) → NULL
```

### Keunggulan

- **Hemat memori**: 1 node fisik, banyak logical views
- **Fleksibel**: Tambah chain baru tanpa membuat duplikat data
- **Akses cepat**: Traversal per-row atau per-column sesuai kebutuhan

---

## 🔁 Complex Iterators

Untuk struktur nested (array of linked lists), iterator perlu melacak **dua state** sekaligus:

```python
class _SparseMatrixIterator:
    def __init__(self, rowArray):
        self._rowArray = rowArray
        self._curRow   = 0      # posisi di array
        self._curNode  = None   # posisi di linked list dalam row
        self._findNextElement()

    def __next__(self):
        if self._curNode is None:
            raise StopIteration
        value = self._curNode.value
        self._curNode = self._curNode.nextRow
        if self._curNode is None:
            self._findNextElement()   # loncat ke row berikutnya
        return value

    def _findNextElement(self):
        while self._curRow < len(self._rowArray):
            if self._rowArray[self._curRow] is not None:
                self._curNode = self._rowArray[self._curRow]
                return
            self._curRow += 1
        self._curNode = None   # iterator habis
```

---

## ✏️ Aplikasi: Text Editor Buffer

### Desain: Doubly Linked List of Vectors

Setiap baris teks disimpan di satu node DLL, dan karakter-karakter dalam baris disimpan di Python list:

```
firstLine → [d,e,f,·,c,o,m,p,u,t,e,S,u,m,·,...,\n]
              ↕
            [·,·,s,u,m,·,=,·,0,\n]
              ↕
            [·,·,f,o,r,·,v,a,l,u,e,·,i,n,...,\n]
              ↕
lastLine  → [·,·,r,e,t,u,r,n,·,s,u,m,\n]
```

### Operasi Penting

```python
# Pecah baris di posisi cursor (breakLine)
def breakLine(self):
    nlContents = self._curLine.text[self._curColNdx:]  # simpan sisa baris
    del self._curLine.text[self._curColNdx:]           # hapus dari baris ini
    self._curLine.text.append('\n')                    # tambah newline
    self._insertNode(self._curLine, nlContents)        # sisipkan baris baru

# Hapus karakter (deleteChar) — dengan merge jika di newline
def deleteChar(self):
    if self.getChar() != '\n':
        self._curLine.text.pop(self._curColNdx)        # hapus biasa
    else:
        if self._curLine is self._lastLine: return     # tidak bisa hapus \n terakhir
        nextLine = self._curLine.next
        self._curLine.text.pop()                       # hapus \n
        self._curLine.text.extend(nextLine.text)       # gabung baris
        self._removeNode(nextLine)
```

---

## 🏋️ Latihan Slide 39: Note-Taking App

Merancang struktur data untuk aplikasi note-taking yang mendukung:

### Kebutuhan & Solusi

| Kebutuhan | Solusi |
|-----------|--------|
| Multiple tags per note | Multi-Linked List via `TagLink` |
| Chronological view | Doubly Linked List sorted by `created_at` |
| Alphabetical view | Doubly Linked List sorted by `title` |
| Sync status tracking | Circular Buffer (fixed-size FIFO) |

### Struktur Node

```python
class NoteNode:
    def __init__(self, note_id, title, content, created_at):
        self.note_id    = note_id
        self.title      = title
        self.content    = content
        self.created_at = created_at

        # Chain 1: Chronological (Doubly Linked)
        self.nextByDate  = None
        self.prevByDate  = None

        # Chain 2: Alphabetical (Doubly Linked)
        self.nextByTitle = None
        self.prevByTitle = None

        # Multi-linked: Tags
        self.firstTag    = None   # → TagLink pertama

class TagLink:
    def __init__(self, tag_name):
        self.tag_name        = tag_name
        self.nextTag         = None    # tag lain pada note ini
        self.nextNoteWithTag = None    # note lain dengan tag yang sama

class CircularSyncBuffer:
    def __init__(self, capacity=5):
        self.buffer   = [None] * capacity
        self.head     = 0   # posisi baca (oldest)
        self.tail     = 0   # posisi tulis
        self.size     = 0
        self.capacity = capacity

    def push(self, record):
        self.buffer[self.tail] = record
        self.tail = (self.tail + 1) % self.capacity
        if self.size < self.capacity:
            self.size += 1
        else:
            self.head = (self.head + 1) % self.capacity  # overwrite oldest
```

### Contoh Output

```
CHRONOLOGICAL VIEW (oldest → newest)
  1. [01/01/25] Belajar Python         tags: #belajar, #python
  2. [02/01/25] Resep Nasi Goreng      tags: #resep, #masakan
  3. [03/01/25] Algoritma Sort         tags: #belajar, #algoritma
  ...

ALPHABETICAL VIEW (A → Z)
  1. Algoritma Sort
  2. Belajar Python
  3. Catatan Belanja
  ...

NOTES BY TAG
  #python    → ['Doubly Linked List', 'Belajar Python']
  #belajar   → ['Algoritma Sort', 'Belajar Python']

CIRCULAR SYNC BUFFER (recent changes)
  [09:30:01] ADD Note#1: Belajar Python
  [09:30:01] ADD Note#2: Algoritma Sort
  ...
```

---

## 📊 Perbandingan Kompleksitas

| Struktur | Insert | Search | Delete | Reverse | Memori |
|----------|--------|--------|--------|---------|--------|
| Singly LL | O(n) | O(n) | O(n) | O(n²) | 1 pointer/node |
| Doubly LL | O(n) | O(n) | **O(1)*** | **O(n)** | 2 pointer/node |
| Circular LL | O(n) | O(n) | O(n) | — | 1 pointer/node |
| Multi-Linked | O(n)×k | O(n) | O(n)×k | — | k pointer/node |

> *O(1) jika referensi node sudah diketahui; k = jumlah chain

---

## 🚀 Cara Menjalankan

### Prasyarat

```bash
pip install matplotlib
```

### Jalankan Demo + Visualisasi

```bash
python note_taking_advanced_linked_list.py
```

Output yang dihasilkan:
- **Terminal**: Hasil traversal chronological, alphabetical, by-tag, dan sync buffer
- **File gambar**: `advanced_linked_list_visualization.png` — visualisasi lengkap semua 4 panel

### Struktur File

```
.
├── note_taking_advanced_linked_list.py   # Implementasi lengkap + visualisasi
└── README.md                             # Dokumentasi ini
```

---

## 📚 Referensi

- *Data Structures & Algorithms Using Python* — Pertemuan 9: Advanced Linked Lists
- [VisuAlgo](https://visualgo.net) — Animasi interaktif struktur data
- [Python Official Docs](https://docs.python.org) — Referensi bahasa Python

---

*Dibuat sebagai materi pembelajaran Struktur Data.*
