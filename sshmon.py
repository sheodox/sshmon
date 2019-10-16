import threading
import gi
import os
from subprocess import Popen
import json
from pathlib import Path

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk


class SSHMonWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="SSH Monitor")

        self.servers = []

        save_dir = os.path.join(Path.home(), '.config/sheodox/sshmon')
        os.makedirs(save_dir, exist_ok=True)
        self.save_path = os.path.join(save_dir, 'servers.json')
        self.load()

        self.list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
        self.add(self.list)

        self.render()

    def save(self):
        info = list({'nn': s.nickname, 'un': s.username, 'hn': s.hostname} for s in self.servers)
        file = open(self.save_path, 'w')
        json.dump(info, file)
        file.close()

    def load(self):
        try:
            file = open(self.save_path, 'r')
            server_info = list(json.load(file))

            file.close()
        except FileNotFoundError:
            server_info = []

        for info in server_info:
            self.servers.append(Server(info['nn'], info['un'], info['hn']))

    def render(self):
        for child in self.list.get_children():
            self.list.remove(child)

        # rows for each server
        for server in self.servers:
            self.create_server_row(server)

        self.render_add_row()

    def create_server_row(self, server):
        def set_button_text(active):
            context = ssh_button.get_style_context()
            context.remove_class('online')
            context.remove_class('pinging')
            context.remove_class('offline')
            context.add_class(active)
            return ssh_button.set_label(f'{server.nickname} - ({server.hostname})')

        box = self.new_box_row()
        ssh_button = Gtk.Button(label='', expand=True)
        delete_button = Gtk.Button(label='Delete')
        set_button_text(server.get_status())

        box.add(ssh_button)
        box.add(delete_button)

        ssh_button.connect("clicked", self.show_ssh, server)
        delete_button.connect("clicked", self.remove_server, server)
        server.ping(set_button_text)

    def render_add_row(self):
        # new server entry
        new_server_box = self.new_box_row()

        nickname_entry = Gtk.Entry()
        nickname_entry.set_placeholder_text('nickname')
        username_entry = Gtk.Entry()
        username_entry.set_placeholder_text('username')
        separator = Gtk.Label(label='@')
        hostname_entry = Gtk.Entry()
        hostname_entry.set_placeholder_text('hostname')
        add = Gtk.Button(label="Add")

        nickname_entry.connect('activate', self.add_server, nickname_entry, username_entry, hostname_entry)
        username_entry.connect('activate', self.add_server, nickname_entry, username_entry, hostname_entry)
        hostname_entry.connect('activate', self.add_server, nickname_entry, username_entry, hostname_entry)
        add.connect('clicked', self.add_server, username_entry, hostname_entry)

        new_server_box.add(nickname_entry)
        new_server_box.add(username_entry)
        new_server_box.add(separator)
        new_server_box.add(hostname_entry)
        new_server_box.add(add)
        self.show_all()

    def add_server(self, widget, nn_entry, un_entry, hn_entry):
        self.servers.append(Server(nn_entry.get_text(), un_entry.get_text(), hn_entry.get_text()))
        self.save()
        self.render()

    def remove_server(self, widget, server):
        self.servers.remove(server)
        self.save()
        self.render()

    def new_list_child(self, child):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        row.add(child)
        self.list.add(row)
        return child

    def new_box_row(self):
        return self.new_list_child(Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, expand=True, spacing=7))

    def show_ssh(self, widget, server):
        if server.get_status() == 'online':
            server.ssh()
        else:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                       f'Cannot connect to {server.hostname}')
            dialog.run()
            dialog.destroy()


class Server:
    def __init__(self, nickname, username, hostname):
        self.nickname = nickname
        self.username = username
        self.hostname = hostname
        self.status = 'pinging'

    def ping(self, callback):
        def in_thread():
            proc = Popen(['/usr/bin/ping', '-c', '1', self.hostname])
            proc.wait()
            was_online = proc.poll() == 0
            self.status = 'online' if was_online else 'offline'
            GLib.idle_add(lambda: callback(self.get_status()))

        thread = threading.Thread(target=in_thread)
        thread.start()

    def get_status(self):
        return self.status

    def ssh(self):
        def ssh(cmd):
            Popen(cmd, shell=True)

        # try to open a terminal depending on which terminal emulators exist on the system
        if os.system('which gnome-terminal') == 0:
            ssh(f'gnome-terminal -- ssh {self.username}@{self.hostname}')
        elif os.system('which konsole') == 0:
            ssh(f'konsole -e "ssh {self.username}@{self.hostname}"')


css_provider = Gtk.CssProvider()
css_provider.load_from_path(str(Path(__file__).resolve().parent.joinpath('style.css')))
screen = Gdk.Screen.get_default()
styleContext = Gtk.StyleContext()
styleContext.add_provider_for_screen(screen, css_provider,
                                     Gtk.STYLE_PROVIDER_PRIORITY_USER)
win = SSHMonWindow()
win.connect('destroy', Gtk.main_quit)
Gtk.main()
