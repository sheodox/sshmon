import gi
import os
from subprocess import Popen
import json
from pathlib import Path

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


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
        info = list({'un': s.username, 'hn': s.hostname} for s in self.servers)
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
            self.servers.append(Server(info['un'], info['hn']))

    def render(self):
        for child in self.list.get_children():
            self.list.remove(child)

        # rows for each row
        for index, server in enumerate(self.servers):
            box = self.new_box_row()
            active = "online" if server.ping() else "offline"
            ssh_button = Gtk.Button(label='{hn} - {active}'.format(hn=server.hostname, active=active), expand=True)
            delete_button = Gtk.Button(label='Delete')

            box.add(ssh_button)
            box.add(delete_button)

            ssh_button.connect("clicked", self.show_ssh, server)
            delete_button.connect("clicked", self.remove_server, server)
        self.render_add_row()

    def render_add_row(self):
        # new server entry
        new_server_box = self.new_box_row()

        username_entry = Gtk.Entry()
        username_entry.set_placeholder_text('username')
        separator = Gtk.Label(label='@')
        hostname_entry = Gtk.Entry()
        hostname_entry.set_placeholder_text('hostname')
        add = Gtk.Button(label="Add")

        username_entry.connect('activate', self.add_server, username_entry, hostname_entry)
        hostname_entry.connect('activate', self.add_server, username_entry, hostname_entry)
        add.connect('clicked', self.add_server, username_entry, hostname_entry)

        new_server_box.add(username_entry)
        new_server_box.add(separator)
        new_server_box.add(hostname_entry)
        new_server_box.add(add)
        self.show_all()

    def add_server(self, widget, un_entry, hn_entry):
        self.servers.append(Server(un_entry.get_text(), hn_entry.get_text()))
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
        if server.ping():
            server.ssh()
        else:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 'Cannot connect to {}'.format(server.hostname))
            dialog.run()
            dialog.destroy()


class Server:

    def __init__(self, username, hostname):
        self.username = username
        self.hostname = hostname
        self.online = os.system('ping -c 1 ' + self.hostname)

    def ping(self):
        return self.online == 0

    def ssh(self):
        def ssh(cmd):
            Popen(cmd, shell=True)
        # try to open a terminal depending on which terminal emulators exist on the system
        if os.system('which gnome-terminal') == 0:
            ssh(f'gnome-terminal -- ssh {self.username}@{self.hostname}')
        elif os.system('which konsole') == 0:
            ssh(f'konsole -e "ssh {self.username}@{self.hostname}"')


win = SSHMonWindow()
win.connect('destroy', Gtk.main_quit)
Gtk.main()
