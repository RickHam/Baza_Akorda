import os
import sys

import tkinter as tk

from tkinter import ttk
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import messagebox

from song_repository import SongRepository
from chord_transpose import transpose_text
from pdf_export import export_pdf


class ChordBook:

    def __init__(self, root):
        self.sorted_songs = []

        self.root = root
        self.root.title("ChordBook")

        self.repo = SongRepository()

        self.current_song = None

        self.build_ui()

        self.load_song_list()

    def build_ui(self):

        self.root.geometry("1400x800")

        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill="x")

        ttk.Button(
            toolbar,
            text="Nova pjesma",
            command=self.new_song
        ).pack(side="left")

        ttk.Button(
            toolbar,
            text="PDF ove pjesme",
            command=self.export_current_pdf
        ).pack(side="left")


        ttk.Button(
            toolbar,
            text="PDF svih pjesama",
            command=self.export_all_pdf
        ).pack(side="left")
        body = ttk.PanedWindow(
            self.root,
            orient="horizontal"
        )

        

        body.pack(fill="both", expand=True)

        left = ttk.Frame(body)

        self.song_list = tk.Listbox(left)

        self.song_list.pack(
            fill="both",
            expand=True
        )

        self.song_list.bind(
            "<<ListboxSelect>>",
            self.on_song_select
        )

        body.add(left, weight=1) #Idk zakaj se smanjenjem weighta poveca prostor

        center = ttk.Frame(body)

        self.editor = tk.Text(
            center,
            font=("Courier New", 12),
            undo=True
        )

        self.editor.pack(
            fill="both",
            expand=True
        )

        self.editor.bind(
            "<KeyRelease>",
            self.autosave
        )

        body.add(center, weight=128)

        right = ttk.Frame(body)

        self.preview = tk.Text(
            right,
            font=("Courier New", 12),
            state="disabled"
        )

        self.preview.pack(
            fill="both",
            expand=True
        )

        body.add(right, weight=128)

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Uredi", command=self.edit_song)

        self.song_list.bind("<Button-3>", self.show_context_menu)


        ttk.Button(
            toolbar,
            text="Transponiraj +1",
            command=lambda: self.transpose(1)
        ).pack(side="left")

        ttk.Button(
            toolbar,
            text="Transponiraj -1",
            command=lambda: self.transpose(-1)
        ).pack(side="left")

        ttk.Button(
            toolbar,
            text="Delete",
            command=self.delete_song
        ).pack(side="left")

        ttk.Button(
            toolbar,
            text="Save",
            command=self.save_song
        ).pack(side="left")


        ttk.Button(
            toolbar,
            text="Refresh",
            command=self.refresh_song
        ).pack(side="left")


    def show_context_menu(self, event):

        try:
            # selektiraj item na koji si kliknuo
            idx = self.song_list.nearest(event.y)
            self.song_list.selection_clear(0, tk.END)
            self.song_list.selection_set(idx)

            self.selected_index = idx

            self.menu.tk_popup(event.x_root, event.y_root)

        finally:
            self.menu.grab_release()

    def edit_song(self):

        if not hasattr(self, "selected_index"):
            return

        song = self.sorted_songs[self.selected_index]

        win = tk.Toplevel(self.root)
        win.title("Uredi pjesmu")
        win.geometry("300x180")
        win.resizable(False, False)

        ttk.Label(win, text="Izvođač:").pack(pady=(10, 0))
        artist_entry = ttk.Entry(win)
        artist_entry.insert(0, song.get("artist", ""))
        artist_entry.pack(fill="x", padx=10)

        ttk.Label(win, text="Pjesma:").pack(pady=(10, 0))
        title_entry = ttk.Entry(win)
        title_entry.insert(0, song.get("title", ""))
        title_entry.pack(fill="x", padx=10)

        def save_changes():

            new_artist = artist_entry.get().strip()
            new_title = title_entry.get().strip()

            if not new_artist or not new_title:
                messagebox.showwarning("Greška", "Popuni oba polja.")
                return

            # update u repo (trebat će ti nova funkcija)
            self.repo.update_song_meta(
                song["id"],
                new_title,
                new_artist
            )

            self.load_song_list()
            win.destroy()

        ttk.Button(win, text="Spremi", command=save_changes).pack(pady=15)

        win.grab_set()
        win.focus_set()
   
    def load_song_list(self):

        

        self.song_list.delete(0, tk.END)

        self.reload_data()

        self.sorted_songs = sorted(
            self.repo.all(),
            key=lambda s: (
                s.get("artist", "").lower(),
                s.get("title", "").lower()
            )
        )

        for song in self.sorted_songs:
            self.song_list.insert(
                tk.END,
                f"{song.get('artist','')} - {song.get('title','')}"
            )

    def reload_data(self):

        self.sorted_songs = sorted(
            self.repo.all(),
            key=lambda s: (
                s.get("artist", "").lower(),
                s.get("title", "").lower()
            )
        )

    def new_song(self):

        win = tk.Toplevel(self.root)
        win.title("Nova pjesma")
        win.geometry("300x180")
        win.resizable(False, False)

        ttk.Label(win, text="Izvođač:").pack(pady=(10, 0))
        artist_entry = ttk.Entry(win)
        artist_entry.pack(fill="x", padx=10)

        ttk.Label(win, text="Pjesma:").pack(pady=(10, 0))
        title_entry = ttk.Entry(win)
        title_entry.pack(fill="x", padx=10)

        def submit():
            artist = artist_entry.get().strip()
            title = title_entry.get().strip()

            if not artist or not title:
                messagebox.showwarning(
                    "Greška",
                    "Popuni oba polja."
                )
                return

            song = self.repo.add_song(
                title,
                artist,
                ""
            )

            self.load_song_list()
            for i, s in enumerate(self.sorted_songs):
                if s["id"] == song["id"]:
                    self.song_list.selection_clear(0, tk.END)
                    self.song_list.selection_set(i)
                    self.song_list.see(i)

                    self.current_song = s
                    self.editor.delete("1.0", tk.END)
                    self.editor.insert("1.0", s["content"])
                    self.update_preview()
                    break
            win.destroy()

        ttk.Button(
            win,
            text="Dodaj",
            command=submit
        ).pack(pady=15)

        win.grab_set()
        win.focus_set()

    def save_song(self):
        if not self.current_song:
            messagebox.showwarning(
                "Save",
                "Nema odabrane pjesme."
            )
            return

        content = self.editor.get("1.0", "end-1c")

        self.repo.update_song(
            self.current_song["id"],
            content
        )

        self.reload_data()

        messagebox.showinfo(
            "Save",
            "Pjesma spremljena."
        )

    def delete_song(self):
        if not self.current_song:
            messagebox.showwarning(
                "Delete",
                "Nema odabrane pjesme."
            )
            return

        confirm = messagebox.askyesno(
            "Potvrda brisanja",
            f"Jesi li siguran da želiš obrisati pjesmu:\n\n{self.current_song['artist']} - {self.current_song['title']}?"
        )

        if not confirm:
            return

        self.repo.delete_song(self.current_song["id"])

        self.current_song = None
        self.editor.delete("1.0", tk.END)
        self.update_preview()
        self.load_song_list()

        messagebox.showinfo(
            "Delete",
            "Pjesma obrisana."
        )

    def on_song_select(self, event):

        sel = self.song_list.curselection()

        if not sel:
            return

        idx = sel[0]

        song = self.sorted_songs[idx]

        self.current_song = song

        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", song["content"])

        self.update_preview()

    def update_preview(self):

        content = self.editor.get(
            "1.0",
            tk.END
        )

        self.preview.config(
            state="normal"
        )

        self.preview.delete(
            "1.0",
            tk.END
        )

        self.preview.insert(
            "1.0",
            content
        )

        self.preview.config(
            state="disabled"
        )

    def autosave(self, event=None):

        self.update_preview()

        if not self.current_song:
            return

        self.repo.update_song(
            self.current_song["id"],
            self.editor.get(
                "1.0",
                tk.END
            )
        )

    def transpose(self, steps):

        txt = self.editor.get(
            "1.0",
            tk.END
        )

        txt = transpose_text(
            txt,
            steps
        )

        self.editor.delete(
            "1.0",
            tk.END
        )

        self.editor.insert(
            "1.0",
            txt
        )


    def export_current_pdf(self):

        if not self.current_song:
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf"
        )

        if not filename:
            return

        export_pdf(
            self.current_song["title"],
            self.editor.get(
                "1.0",
                tk.END
            ),
            filename
        )

        open_file = messagebox.askyesno(
    "PDF",
    "PDF je uspješno spremljen.\n\nŽeliš li ga otvoriti?"
)

        if open_file:
            if sys.platform == "win32":
                os.startfile(filename)
            elif sys.platform == "darwin":
                os.system(f"open '{filename}'")
            else:
                os.system(f"xdg-open '{filename}'")

    def export_all_pdf(self):

        songs = self.repo.all()

        if not songs:
            messagebox.showwarning(
                "PDF",
                    "Nema pjesama za export."
            )
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf"
        )

        if not filename:
            return

        content = ""

        for song in songs:
            content += f"{song['artist']} - {song['title']}\n\n"
            content += song["content"]
            content += "\n\n\f\n"

        export_pdf(
            "Sve pjesme",
            songs,
            filename
        )

        open_file = messagebox.askyesno(
    "PDF",
    "PDF je uspješno spremljen.\n\nŽeliš li ga otvoriti?"
)

        if open_file:
            if sys.platform == "win32":
                os.startfile(filename)
            elif sys.platform == "darwin":
                os.system(f"open '{filename}'")
            else:
                os.system(f"xdg-open '{filename}'")
    def refresh_song(self):

        if not self.current_song:
            messagebox.showwarning(
                "Refresh",
                "Nema odabrane pjesme."
            )
            return

        confirm = messagebox.askyesno(
            "Potvrda refresh-a",
            "Jeste li sigurni da želite refresh?\n\nSve nespremljene promjene će biti izgubljene."
        )

        if not confirm:
            return

        songs = self.repo.all()

        fresh_song = None

        for song in songs:
            if song["id"] == self.current_song["id"]:
                fresh_song = song
                break

        if not fresh_song:
            messagebox.showerror(
                "Refresh",
                "Pjesma ne postoji u bazi."
            )
            return

        self.current_song = fresh_song

        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", fresh_song["content"])

        self.update_preview()



root = tk.Tk()

app = ChordBook(root)

root.mainloop()