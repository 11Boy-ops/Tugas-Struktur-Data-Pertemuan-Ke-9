"""
=============================================================================
LATIHAN SLIDE 39 - Advanced Linked Lists
=============================================================================
Rancang struktur data untuk aplikasi note-taking yang mendukung:
  1. Multiple tags per note    → Multi-Linked List (by tag)
  2. Chronological view        → Doubly Linked List (sorted by date)
  3. Alphabetical view         → Doubly Linked List (sorted by title)
  4. Sync status tracking      → Circular Buffer untuk recent changes
=============================================================================
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import matplotlib.gridspec as gridspec
from datetime import datetime, timedelta
import random
import textwrap

# ─────────────────────────────────────────────────────────────────────────────
#  BAGIAN 1: STRUKTUR DATA (NODE DEFINITIONS)
# ─────────────────────────────────────────────────────────────────────────────

class NoteNode:
    """
    Node utama untuk setiap catatan.
    Mengandung MULTIPLE link fields untuk mendukung:
      - nextByDate / prevByDate  : Doubly linked chain (chronological)
      - nextByTitle / prevByTitle: Doubly linked chain (alphabetical)
      - firstTag                 : pointer ke TagLink pertama note ini
    """
    def __init__(self, note_id, title, content, created_at):
        self.note_id   = note_id
        self.title     = title
        self.content   = content
        self.created_at = created_at  # datetime object

        # Chain 1: Chronological (Doubly Linked, sorted by date)
        self.nextByDate = None
        self.prevByDate = None

        # Chain 2: Alphabetical (Doubly Linked, sorted by title)
        self.nextByTitle = None
        self.prevByTitle = None

        # Pointer ke daftar tag milik note ini (multi-linked)
        self.firstTag = None

    def __repr__(self):
        return f"Note({self.note_id}: '{self.title}' @ {self.created_at.strftime('%d/%m/%y')})"


class TagLink:
    """
    Node penghubung antara Note dan Tag.
    Setiap note bisa memiliki banyak TagLink (multi-linked by tag).
    """
    def __init__(self, tag_name):
        self.tag_name   = tag_name
        self.nextTag    = None   # tag berikutnya pada note yang sama
        self.nextNoteWithTag = None  # note berikutnya yang punya tag ini


class TagHead:
    """
    Head pointer untuk setiap tag unik.
    Menyimpan referensi ke note pertama dengan tag tersebut.
    """
    def __init__(self, tag_name):
        self.tag_name   = tag_name
        self.firstNote  = None   # note pertama dengan tag ini
        self.count      = 0      # jumlah note dengan tag ini


class CircularSyncBuffer:
    """
    Circular Buffer untuk tracking sync status perubahan terbaru.
    Digunakan untuk: Undo, recent-changes, sync queue.
    Implementasi: Fixed-size circular array dengan head & tail pointer.
    """
    def __init__(self, capacity=5):
        self.capacity  = capacity
        self.buffer    = [None] * capacity
        self.head      = 0    # posisi baca (oldest)
        self.tail      = 0    # posisi tulis (next write)
        self.size      = 0    # jumlah elemen aktif

    def push(self, change_record):
        """Tambah perubahan baru ke buffer (overwrite jika penuh)."""
        self.buffer[self.tail] = change_record
        self.tail = (self.tail + 1) % self.capacity
        if self.size < self.capacity:
            self.size += 1
        else:
            # Overwrite oldest → geser head
            self.head = (self.head + 1) % self.capacity

    def pop(self):
        """Ambil perubahan terlama (FIFO)."""
        if self.size == 0:
            return None
        record = self.buffer[self.head]
        self.buffer[self.head] = None
        self.head = (self.head + 1) % self.capacity
        self.size -= 1
        return record

    def get_all(self):
        """Kembalikan semua perubahan dalam urutan masuk."""
        result = []
        for i in range(self.size):
            idx = (self.head + i) % self.capacity
            result.append(self.buffer[idx])
        return result

    def is_empty(self):
        return self.size == 0

    def is_full(self):
        return self.size == self.capacity


# ─────────────────────────────────────────────────────────────────────────────
#  BAGIAN 2: NOTE-TAKING APP (Manajemen Semua Struktur)
# ─────────────────────────────────────────────────────────────────────────────

class NoteTakingApp:
    """
    Aplikasi note-taking dengan 3 struktur data utama:
      1. headByDate / tailByDate   : Doubly LL sorted chronologically
      2. headByTitle / tailByTitle : Doubly LL sorted alphabetically
      3. tag_heads (dict)          : Multi-linked list by tag
      4. sync_buffer               : Circular buffer recent changes
    """

    def __init__(self, sync_buffer_size=5):
        # Chain chronological
        self.headByDate  = None
        self.tailByDate  = None

        # Chain alphabetical
        self.headByTitle = None
        self.tailByTitle = None

        # Tag index: tag_name → TagHead
        self.tag_heads   = {}

        # Circular sync buffer
        self.sync_buffer = CircularSyncBuffer(sync_buffer_size)

        self._next_id    = 1

    # ── INSERT ─────────────────────────────────────────────────────────────

    def add_note(self, title, content, tags, created_at=None):
        """Tambahkan note baru ke semua chain sekaligus."""
        if created_at is None:
            created_at = datetime.now()

        note = NoteNode(self._next_id, title, content, created_at)
        self._next_id += 1

        # Insert ke chain by date
        self._insert_by_date(note)

        # Insert ke chain by title
        self._insert_by_title(note)

        # Insert ke multi-linked tag chains
        for tag in tags:
            self._insert_tag(note, tag)

        # Catat perubahan ke circular buffer
        self.sync_buffer.push({
            "action": "ADD",
            "note_id": note.note_id,
            "title": title,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

        return note

    def _insert_by_date(self, note):
        """Insert node ke doubly linked list sorted by created_at."""
        if self.headByDate is None:
            self.headByDate = self.tailByDate = note
            return

        if note.created_at <= self.headByDate.created_at:
            note.nextByDate = self.headByDate
            self.headByDate.prevByDate = note
            self.headByDate = note
            return

        if note.created_at >= self.tailByDate.created_at:
            note.prevByDate = self.tailByDate
            self.tailByDate.nextByDate = note
            self.tailByDate = note
            return

        cur = self.headByDate
        while cur is not None and cur.created_at < note.created_at:
            cur = cur.nextByDate

        note.nextByDate = cur
        note.prevByDate = cur.prevByDate
        cur.prevByDate.nextByDate = note
        cur.prevByDate = note

    def _insert_by_title(self, note):
        """Insert node ke doubly linked list sorted alphabetically by title."""
        if self.headByTitle is None:
            self.headByTitle = self.tailByTitle = note
            return

        if note.title.lower() <= self.headByTitle.title.lower():
            note.nextByTitle = self.headByTitle
            self.headByTitle.prevByTitle = note
            self.headByTitle = note
            return

        if note.title.lower() >= self.tailByTitle.title.lower():
            note.prevByTitle = self.tailByTitle
            self.tailByTitle.nextByTitle = note
            self.tailByTitle = note
            return

        cur = self.headByTitle
        while cur is not None and cur.title.lower() < note.title.lower():
            cur = cur.nextByTitle

        note.nextByTitle = cur
        note.prevByTitle = cur.prevByTitle
        cur.prevByTitle.nextByTitle = note
        cur.prevByTitle = note

    def _insert_tag(self, note, tag_name):
        """Tambahkan tag ke note dan update tag head index."""
        tag_link = TagLink(tag_name)

        # Tambah ke daftar tag note ini (prepend)
        tag_link.nextTag = note.firstTag
        note.firstTag = tag_link

        # Update tag head index
        if tag_name not in self.tag_heads:
            self.tag_heads[tag_name] = TagHead(tag_name)

        th = self.tag_heads[tag_name]
        tag_link.nextNoteWithTag = th.firstNote
        th.firstNote = note
        th.count += 1

    # ── TRAVERSAL ──────────────────────────────────────────────────────────

    def get_notes_chronological(self):
        """Traverse chain by date (oldest → newest)."""
        result, cur = [], self.headByDate
        while cur:
            result.append(cur)
            cur = cur.nextByDate
        return result

    def get_notes_alphabetical(self):
        """Traverse chain by title (A → Z)."""
        result, cur = [], self.headByTitle
        while cur:
            result.append(cur)
            cur = cur.nextByTitle
        return result

    def get_notes_by_tag(self, tag_name):
        """Kembalikan semua note yang memiliki tag tertentu."""
        if tag_name not in self.tag_heads:
            return []
        result, cur = [], self.tag_heads[tag_name].firstNote
        while cur:
            result.append(cur)
            # Cari TagLink yang sesuai untuk ikuti nextNoteWithTag
            tl = cur.firstTag
            found_next = None
            while tl:
                if tl.tag_name == tag_name:
                    found_next = tl.nextNoteWithTag
                    break
                tl = tl.nextTag
            cur = found_next
        return result

    def get_recent_changes(self):
        """Kembalikan perubahan terbaru dari circular buffer."""
        return self.sync_buffer.get_all()


# ─────────────────────────────────────────────────────────────────────────────
#  BAGIAN 3: DEMO DATA
# ─────────────────────────────────────────────────────────────────────────────

def build_demo_app():
    app = NoteTakingApp(sync_buffer_size=5)
    base = datetime(2025, 1, 1, 9, 0)

    notes_data = [
        ("Belajar Python",    "Materi OOP dan list comprehension",   ["python", "belajar"], 0),
        ("Algoritma Sort",    "Bubble, Merge, Quick Sort",           ["algoritma", "belajar"], 2),
        ("Resep Nasi Goreng", "Cara masak nasi goreng spesial",      ["masakan", "resep"], 1),
        ("Meeting Notes",    "Agenda rapat proyek semester",         ["kerja", "meeting"], 4),
        ("Doubly Linked List","Implementasi DLL dengan Python",      ["python", "algoritma"], 3),
        ("Catatan Belanja",   "Beli beras, sayur, minyak goreng",    ["belanja", "rumah"], 5),
    ]

    for title, content, tags, day_offset in notes_data:
        app.add_note(title, content, tags,
                     created_at=base + timedelta(days=day_offset))
    return app


# ─────────────────────────────────────────────────────────────────────────────
#  BAGIAN 4: VISUALISASI
# ─────────────────────────────────────────────────────────────────────────────

COLORS = {
    "node_date"    : "#4A90D9",
    "node_title"   : "#27AE60",
    "node_tag"     : "#E67E22",
    "node_circ"    : "#8E44AD",
    "arrow_fwd"    : "#2C3E50",
    "arrow_bwd"    : "#E74C3C",
    "arrow_tag"    : "#E67E22",
    "bg"           : "#F8F9FA",
    "title_bg"     : "#2C3E50",
    "text_light"   : "white",
    "text_dark"    : "#2C3E50",
    "highlight"    : "#F39C12",
    "empty"        : "#BDC3C7",
}


def draw_node(ax, x, y, label, sublabel="", color="#4A90D9",
              width=2.2, height=0.7, fontsize=8):
    """Gambar satu node sebagai kotak berwarna."""
    box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                         boxstyle="round,pad=0.05",
                         facecolor=color, edgecolor="white",
                         linewidth=1.5, zorder=3)
    ax.add_patch(box)
    ax.text(x, y + 0.08, label, ha="center", va="center",
            fontsize=fontsize, fontweight="bold",
            color="white", zorder=4, wrap=True)
    if sublabel:
        ax.text(x, y - 0.18, sublabel, ha="center", va="center",
                fontsize=fontsize - 1.5, color="#ECF0F1", zorder=4)


def draw_arrow(ax, x1, y1, x2, y2, color="#2C3E50",
               style="->", lw=1.5, label=""):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color,
                                lw=lw, connectionstyle="arc3,rad=0.0"),
                zorder=2)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my+0.1, label, fontsize=6, color=color, ha="center")


def visualize_all(app):
    fig = plt.figure(figsize=(20, 22), facecolor=COLORS["bg"])
    gs = gridspec.GridSpec(4, 1, figure=fig,
                           hspace=0.45,
                           top=0.95, bottom=0.03,
                           left=0.04, right=0.96)

    # ── Panel header ──────────────────────────────────────────────────────
    fig.text(0.5, 0.975,
             "Note-Taking App — Advanced Linked List (Slide 39)",
             ha="center", va="top", fontsize=16, fontweight="bold",
             color=COLORS["text_dark"])

    # ─────────────────────────────────────────────────────────────────────
    #  PANEL 1: Chronological Doubly Linked List
    # ─────────────────────────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0])
    ax1.set_xlim(0, 20)
    ax1.set_ylim(-0.8, 1.5)
    ax1.axis("off")
    ax1.set_facecolor(COLORS["bg"])

    ax1.text(0.3, 1.35, "Chain 1: Chronological View (Doubly Linked List, sorted by date)",
             fontsize=11, fontweight="bold", color=COLORS["node_date"],
             transform=ax1.transAxes, va="top")
    ax1.text(0.3, 1.10,
             "HEAD ◄──────────────────────────────────────────────────────► TAIL",
             fontsize=7, color="#7F8C8D", transform=ax1.transAxes, va="top")

    notes_chron = app.get_notes_chronological()
    xs = [i * 3.0 + 1.5 for i in range(len(notes_chron))]
    y_main = 0.5

    # Draw NULL left
    ax1.text(xs[0] - 2.0, y_main, "NULL", fontsize=8, color=COLORS["empty"],
             ha="center", va="center", style="italic")

    for i, note in enumerate(notes_chron):
        short = textwrap.shorten(note.title, width=14, placeholder="…")
        draw_node(ax1, xs[i], y_main,
                  short,
                  note.created_at.strftime("%d/%m/%y"),
                  color=COLORS["node_date"])

        # Forward arrow (next)
        if i < len(notes_chron) - 1:
            draw_arrow(ax1, xs[i] + 1.1, y_main + 0.15,
                       xs[i+1] - 1.1, y_main + 0.15,
                       color=COLORS["arrow_fwd"], style="-|>")
        # Backward arrow (prev)
        if i > 0:
            draw_arrow(ax1, xs[i] - 1.1, y_main - 0.15,
                       xs[i-1] + 1.1, y_main - 0.15,
                       color=COLORS["arrow_bwd"], style="-|>")

    # Draw NULL right
    ax1.text(xs[-1] + 2.0, y_main, "NULL", fontsize=8, color=COLORS["empty"],
             ha="center", va="center", style="italic")

    # Legend
    leg = [
        mpatches.Patch(color=COLORS["arrow_fwd"], label=".nextByDate →"),
        mpatches.Patch(color=COLORS["arrow_bwd"], label="← .prevByDate"),
    ]
    ax1.legend(handles=leg, loc="lower right", fontsize=8,
               framealpha=0.8, ncol=2)

    # ─────────────────────────────────────────────────────────────────────
    #  PANEL 2: Alphabetical Doubly Linked List
    # ─────────────────────────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1])
    ax2.set_xlim(0, 20)
    ax2.set_ylim(-0.8, 1.5)
    ax2.axis("off")
    ax2.set_facecolor(COLORS["bg"])

    ax2.text(0.3, 1.35, "Chain 2: Alphabetical View (Doubly Linked List, sorted by title)",
             fontsize=11, fontweight="bold", color=COLORS["node_title"],
             transform=ax2.transAxes, va="top")

    notes_alpha = app.get_notes_alphabetical()
    xs2 = [i * 3.0 + 1.5 for i in range(len(notes_alpha))]

    ax2.text(xs2[0] - 2.0, 0.5, "NULL", fontsize=8, color=COLORS["empty"],
             ha="center", va="center", style="italic")

    for i, note in enumerate(notes_alpha):
        short = textwrap.shorten(note.title, width=14, placeholder="…")
        draw_node(ax2, xs2[i], 0.5,
                  short,
                  f"[{chr(65 + i)}]",
                  color=COLORS["node_title"])

        if i < len(notes_alpha) - 1:
            draw_arrow(ax2, xs2[i] + 1.1, 0.65,
                       xs2[i+1] - 1.1, 0.65,
                       color=COLORS["arrow_fwd"], style="-|>")
        if i > 0:
            draw_arrow(ax2, xs2[i] - 1.1, 0.35,
                       xs2[i-1] + 1.1, 0.35,
                       color=COLORS["arrow_bwd"], style="-|>")

    ax2.text(xs2[-1] + 2.0, 0.5, "NULL", fontsize=8, color=COLORS["empty"],
             ha="center", va="center", style="italic")

    leg2 = [
        mpatches.Patch(color=COLORS["arrow_fwd"], label=".nextByTitle →"),
        mpatches.Patch(color=COLORS["arrow_bwd"], label="← .prevByTitle"),
    ]
    ax2.legend(handles=leg2, loc="lower right", fontsize=8,
               framealpha=0.8, ncol=2)

    # ─────────────────────────────────────────────────────────────────────
    #  PANEL 3: Multi-Linked Tags
    # ─────────────────────────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[2])
    ax3.set_xlim(0, 20)
    ax3.set_ylim(-1.5, 3.0)
    ax3.axis("off")
    ax3.set_facecolor(COLORS["bg"])

    ax3.text(0.3, 1.05, "Chain 3: Multi-Linked by Tags (Tag Index)",
             fontsize=11, fontweight="bold", color=COLORS["node_tag"],
             transform=ax3.transAxes, va="top")

    # Ambil beberapa tag untuk ditampilkan
    tags_to_show = ["python", "belajar", "algoritma"]
    tag_y_positions = {t: 2.2 - i * 1.3 for i, t in enumerate(tags_to_show)}

    for tag in tags_to_show:
        ty = tag_y_positions[tag]
        # Gambar tag head
        tag_box = FancyBboxPatch((-0.1, ty - 0.28), 1.8, 0.56,
                                  boxstyle="round,pad=0.05",
                                  facecolor="#E67E22",
                                  edgecolor="white", linewidth=1.5, zorder=3)
        ax3.add_patch(tag_box)
        ax3.text(0.8, ty, f"#{tag}", ha="center", va="center",
                 fontsize=9, fontweight="bold", color="white", zorder=4)

        # Gambar note yang punya tag ini
        notes_with_tag = app.get_notes_by_tag(tag)
        for j, note in enumerate(notes_with_tag):
            nx = 2.5 + j * 3.5
            # Kotak note kecil
            nb = FancyBboxPatch((nx - 1.5, ty - 0.28), 2.8, 0.56,
                                 boxstyle="round,pad=0.05",
                                 facecolor="#3498DB",
                                 edgecolor="white", linewidth=1.2, zorder=3)
            ax3.add_patch(nb)
            short = textwrap.shorten(note.title, width=14, placeholder="…")
            ax3.text(nx - 0.1, ty, short, ha="center", va="center",
                     fontsize=7.5, color="white", zorder=4)

            # Arrow dari tag head atau note sebelumnya
            if j == 0:
                draw_arrow(ax3, 1.7, ty, nx - 1.5, ty,
                           color=COLORS["arrow_tag"], style="-|>", lw=1.5)
            else:
                prev_nx = 2.5 + (j-1) * 3.5
                draw_arrow(ax3, prev_nx + 1.3, ty, nx - 1.5, ty,
                           color=COLORS["arrow_tag"], style="-|>", lw=1.5)

        # NULL di akhir
        if notes_with_tag:
            last_nx = 2.5 + (len(notes_with_tag)-1) * 3.5
            ax3.text(last_nx + 2.0, ty, "NULL", fontsize=7,
                     color=COLORS["empty"], ha="center", va="center",
                     style="italic")

    # ─────────────────────────────────────────────────────────────────────
    #  PANEL 4: Circular Sync Buffer
    # ─────────────────────────────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[3])
    ax4.set_xlim(-1, 21)
    ax4.set_ylim(-2.5, 3.5)
    ax4.axis("off")
    ax4.set_facecolor(COLORS["bg"])

    ax4.text(0.3, 1.05, "Circular Buffer: Sync / Recent Changes Tracker",
             fontsize=11, fontweight="bold", color=COLORS["node_circ"],
             transform=ax4.transAxes, va="top")

    # Gambar slot circular buffer sebagai kotak berurutan
    buf = app.sync_buffer
    cap = buf.capacity
    changes = buf.get_all()
    slot_w, slot_h = 3.2, 1.0
    start_x = 1.0

    for i in range(cap):
        sx = start_x + i * (slot_w + 0.4)
        sy = 0.5
        idx_in_buf = (buf.head + i) % cap
        is_active = i < buf.size

        color = COLORS["node_circ"] if is_active else COLORS["empty"]
        box = FancyBboxPatch((sx, sy - slot_h/2), slot_w, slot_h,
                              boxstyle="round,pad=0.05",
                              facecolor=color,
                              edgecolor="white", linewidth=2, zorder=3)
        ax4.add_patch(box)

        # Label slot
        if is_active and i < len(changes):
            ch = changes[i]
            ax4.text(sx + slot_w/2, sy + 0.2,
                     f"{ch['action']}: {textwrap.shorten(ch['title'], 12, placeholder='…')}",
                     ha="center", va="center", fontsize=7.5,
                     fontweight="bold", color="white", zorder=4)
            ax4.text(sx + slot_w/2, sy - 0.2,
                     f"ID:{ch['note_id']}  {ch['timestamp']}",
                     ha="center", va="center", fontsize=6.5,
                     color="#ECF0F1", zorder=4)
        else:
            ax4.text(sx + slot_w/2, sy, "[EMPTY]",
                     ha="center", va="center", fontsize=8,
                     color="white", zorder=4, style="italic")

        # Slot index label
        ax4.text(sx + slot_w/2, sy - 0.72, f"Slot {i}",
                 ha="center", va="top", fontsize=7, color="#7F8C8D")

        # Circular arrow dari slot terakhir ke pertama
        if i < cap - 1:
            ax4.annotate("",
                xy=(sx + slot_w + 0.4, sy),
                xytext=(sx + slot_w, sy),
                arrowprops=dict(arrowstyle="-|>",
                                color=COLORS["node_circ"],
                                lw=1.5),
                zorder=2)

    # Loopback arrow dari slot terakhir ke pertama
    last_sx = start_x + (cap-1) * (slot_w + 0.4)
    ax4.annotate("",
        xy=(start_x + slot_w/2, sy - slot_h/2 - 0.9),
        xytext=(last_sx + slot_w/2, sy - slot_h/2 - 0.9),
        arrowprops=dict(arrowstyle="<-",
                        color=COLORS["node_circ"],
                        lw=2.0,
                        connectionstyle="arc3,rad=0.0"),
        zorder=2)
    ax4.plot([start_x + slot_w/2, start_x + slot_w/2],
             [sy - slot_h/2, sy - slot_h/2 - 0.9],
             color=COLORS["node_circ"], lw=1.5)
    ax4.plot([last_sx + slot_w/2, last_sx + slot_w/2],
             [sy - slot_h/2, sy - slot_h/2 - 0.9],
             color=COLORS["node_circ"], lw=1.5)
    ax4.text((start_x + last_sx + slot_w) / 2, sy - slot_h/2 - 1.1,
             "↩  Circular Wrap-Around (FIFO, Overwrite on Full)",
             ha="center", va="top", fontsize=8, color=COLORS["node_circ"],
             style="italic")

    # HEAD / TAIL labels
    head_sx = start_x + buf.head * (slot_w + 0.4)
    tail_sx = start_x + ((buf.tail - 1) % cap) * (slot_w + 0.4)
    ax4.text(head_sx + slot_w/2, sy + slot_h/2 + 0.15,
             "▼ HEAD\n(oldest)", ha="center", va="bottom",
             fontsize=7.5, color="#27AE60", fontweight="bold")
    ax4.text(tail_sx + slot_w/2, sy + slot_h/2 + 0.15,
             "▼ TAIL\n(newest)", ha="center", va="bottom",
             fontsize=7.5, color="#E74C3C", fontweight="bold")

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "advanced_linked_list_visualization.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=COLORS["bg"])
    plt.close()
    print(f"✅ Visualisasi disimpan di: {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
#  BAGIAN 5: DEMO PRINT
# ─────────────────────────────────────────────────────────────────────────────

def print_demo(app):
    sep = "─" * 60

    print(f"\n{'═'*60}")
    print("  NOTE-TAKING APP — Advanced Linked List Demo")
    print(f"{'═'*60}")

    print(f"\n{sep}")
    print("  ⏱️  CHRONOLOGICAL VIEW (oldest → newest)")
    print(sep)
    for i, n in enumerate(app.get_notes_chronological(), 1):
        tags = _get_tags(n)
        print(f"  {i}. [{n.created_at.strftime('%d/%m/%y')}] {n.title:<25}  tags: {tags}")

    print(f"\n{sep}")
    print("  🔤  ALPHABETICAL VIEW (A → Z)")
    print(sep)
    for i, n in enumerate(app.get_notes_alphabetical(), 1):
        print(f"  {i}. {n.title}")

    print(f"\n{sep}")
    print("  🏷️  NOTES BY TAG")
    print(sep)
    for tag in ["python", "belajar", "algoritma"]:
        notes = app.get_notes_by_tag(tag)
        titles = [n.title for n in notes]
        print(f"  #{tag:<12} → {titles}")

    print(f"\n{sep}")
    print("  🔄  RECENT CHANGES (Circular Buffer)")
    print(sep)
    for ch in app.get_recent_changes():
        print(f"  [{ch['timestamp']}] {ch['action']} Note#{ch['note_id']}: {ch['title']}")

    print(f"\n{'═'*60}\n")


def _get_tags(note):
    tags, tl = [], note.firstTag
    while tl:
        tags.append(f"#{tl.tag_name}")
        tl = tl.nextTag
    return ", ".join(tags)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = build_demo_app()
    print_demo(app)
    visualize_all(app)
