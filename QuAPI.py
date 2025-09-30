import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
from requests.auth import HTTPBasicAuth
import json
import xml.etree.ElementTree as ET
from datetime import datetime

class QualysAPIClient:
    def __init__(self, root):
        self.root = root
        self.root.title("QuAPI - Qualys API Client")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)

        # --- Enhanced Color Theme ---
        self.bg_grey_dark = "#1e1e1e"
        self.bg_grey_medium = "#2d2d2d"
        self.bg_grey_light = "#3c3c3c"
        self.maroon = "#8b0000"
        self.maroon_light = "#a52a2a"
        self.maroon_hover = "#b33030"
        self.text_white = "#e8e8e8"
        self.text_grey = "#b0b0b0"
        self.accent_blue = "#4a9eff"

        self.root.configure(bg=self.bg_grey_dark)

        # --- Enhanced Style Configuration ---
        style = ttk.Style()
        style.theme_use('clam')

        # Frame styles
        style.configure('TFrame', background=self.bg_grey_dark)
        style.configure('Card.TFrame', background=self.bg_grey_medium, relief=tk.FLAT)

        # Label styles
        style.configure('TLabel', background=self.bg_grey_dark, foreground=self.text_white, font=('Segoe UI', 9))
        style.configure('Title.TLabel', font=('Segoe UI', 11, 'bold'), foreground=self.maroon_light)
        style.configure('Header.TLabel', font=('Segoe UI', 10, 'bold'), foreground=self.text_white)

        # Button styles
        style.configure('TButton',
            background=self.maroon,
            foreground=self.text_white,
            borderwidth=0,
            padding=(8, 4),
            font=('Segoe UI', 8))
        style.map('TButton',
            background=[('active', self.maroon_hover), ('pressed', self.maroon_light)],
            relief=[('pressed', 'sunken')])

        style.configure('Action.TButton',
            background=self.accent_blue,
            foreground=self.text_white,
            font=('Segoe UI', 9, 'bold'))
        style.map('Action.TButton',
            background=[('active', '#3a8eef')])

        # Entry styles
        style.configure('TEntry',
            fieldbackground=self.bg_grey_light,
            foreground=self.text_white,
            bordercolor=self.maroon,
            insertcolor=self.text_white,
            padding=5)

        # Combobox styles
        style.configure('TCombobox',
            fieldbackground=self.bg_grey_light,
            background=self.bg_grey_light,
            foreground=self.text_white,
            bordercolor=self.maroon,
            arrowcolor=self.text_white,
            padding=5)
        style.map('TCombobox',
            fieldbackground=[('readonly', self.bg_grey_light)],
            selectbackground=[('readonly', self.bg_grey_light)])

        # Radio button styles
        style.configure('TRadiobutton',
            background=self.bg_grey_medium,
            foreground=self.text_white,
            font=('Segoe UI', 9))

        # LabelFrame styles
        style.configure('TLabelframe',
            background=self.bg_grey_dark,
            bordercolor=self.maroon,
            borderwidth=2)
        style.configure('TLabelframe.Label',
            background=self.bg_grey_dark,
            foreground=self.maroon_light,
            font=('Segoe UI', 10, 'bold'))

        # Notebook styles
        style.configure('TNotebook',
            background=self.bg_grey_dark,
            borderwidth=0,
            tabmargins=[2, 5, 2, 0])
        style.configure('TNotebook.Tab',
            background=self.bg_grey_medium,
            foreground=self.text_grey,
            padding=[15, 8],
            font=('Segoe UI', 9))
        style.map('TNotebook.Tab',
            background=[('selected', self.maroon)],
            foreground=[('selected', self.text_white)],
            expand=[('selected', [1, 1, 1, 0])])

        # Treeview styles
        style.configure('Treeview',
            background=self.bg_grey_medium,
            foreground=self.text_white,
            fieldbackground=self.bg_grey_medium,
            borderwidth=0,
            font=('Segoe UI', 9))
        style.configure('Treeview.Heading',
            background=self.maroon,
            foreground=self.text_white,
            borderwidth=0,
            font=('Segoe UI', 9, 'bold'))
        style.map('Treeview.Heading',
            background=[('active', self.maroon_light)])
        style.map('Treeview',
            background=[('selected', self.maroon_light)],
            foreground=[('selected', self.text_white)])

        # Scrollbar styles
        style.configure('Vertical.TScrollbar',
            background=self.bg_grey_medium,
            troughcolor=self.bg_grey_dark,
            borderwidth=0,
            arrowcolor=self.text_white)

        # Cache for templates and other data
        self.report_templates = {}
        self.scan_refs = {}

        # --- Main Container ---
        main_container = ttk.Frame(root, style='TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- API Configuration Section ---
        config_frame = ttk.LabelFrame(main_container, text="API Configuration", padding=15)
        config_frame.pack(fill=tk.X, padx=5, pady=5)

        # API URL
        ttk.Label(config_frame, text="API URL:", style='TLabel').grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.api_url = ttk.Entry(config_frame, width=60, style='TEntry')
        self.api_url.insert(0, "https://qualysguard.qg1.apps.qualys.co.uk")
        self.api_url.grid(row=0, column=1, pady=5, sticky=tk.EW)

        # Username
        ttk.Label(config_frame, text="Username:", style='TLabel').grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.username = ttk.Entry(config_frame, width=60, style='TEntry')
        self.username.grid(row=1, column=1, pady=5, sticky=tk.EW)

        # Password
        ttk.Label(config_frame, text="Password:", style='TLabel').grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.password = ttk.Entry(config_frame, width=60, show="*", style='TEntry')
        self.password.grid(row=2, column=1, pady=5, sticky=tk.EW)

        config_frame.columnconfigure(1, weight=1)

        # --- Operations Area ---
        operations_container = ttk.Frame(main_container, style='TFrame')
        operations_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Sidebar with Operations ---
        sidebar = ttk.Frame(operations_container, style='Card.TFrame', width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        sidebar.pack_propagate(False)

        # Sidebar header
        sidebar_header = ttk.Label(sidebar, text="API Operations", style='Title.TLabel')
        sidebar_header.pack(pady=(10, 15), padx=10)

        # Create scrollable button area
        button_canvas = tk.Canvas(sidebar, bg=self.bg_grey_medium, highlightthickness=0)
        button_scrollbar = ttk.Scrollbar(sidebar, orient="vertical", command=button_canvas.yview)
        button_frame = ttk.Frame(button_canvas, style='Card.TFrame')

        button_frame.bind(
            "<Configure>",
            lambda e: button_canvas.configure(scrollregion=button_canvas.bbox("all"))
        )

        button_canvas.create_window((0, 0), window=button_frame, anchor="nw")
        button_canvas.configure(yscrollcommand=button_scrollbar.set)

        button_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        button_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Button Groups ---
        button_groups = {
            "Vulnerability Management": [
                ("List Scans", self.list_scans),
                ("Launch Scan", self.launch_scan),
                ("Get Scan Results", self.get_scan_results),
                ("List Scan Targets", self.list_scan_targets)
            ],
            "Asset Management": [
                ("Search Assets", self.search_assets),
                ("List Cloud Agents", self.list_agents),
                ("Get Host Details", self.get_host_details),
                ("List Activation Keys", self.list_activation_keys)
            ],
            "Reports": [
                ("List Reports", self.list_reports),
                ("List Report Templates", self.list_report_templates),
                ("Launch Report", self.launch_report),
                ("Fetch Report", self.fetch_report),
                ("Delete Report", self.delete_report)
            ],
            "Knowledge Base": [
                ("Search Vulnerabilities", self.search_vulnerabilities),
                ("Get QID Details", self.get_qid_details)
            ],
            "Utilities": [
                ("Get User Info", self.get_user_info),
                ("Custom Request", self.custom_request),
                ("Clear Output", self.clear_output)
            ]
        }

        for group_name, buttons in button_groups.items():
            # Group label
            group_label = ttk.Label(button_frame, text=group_name, style='Header.TLabel')
            group_label.pack(anchor=tk.W, pady=(8, 4), padx=10)

            # Separator
            separator = ttk.Separator(button_frame, orient='horizontal')
            separator.pack(fill=tk.X, padx=10, pady=(0, 4))

            # Buttons
            for btn_text, btn_command in buttons:
                btn = ttk.Button(button_frame, text=btn_text, command=btn_command, style='TButton')
                btn.pack(fill=tk.X, pady=2, padx=10)

        # --- Output Area ---
        output_frame = ttk.Frame(operations_container, style='TFrame')
        output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Output notebook with tabs
        self.output_notebook = ttk.Notebook(output_frame)
        self.output_notebook.pack(fill=tk.BOTH, expand=True)

        # Formatted Output Tab
        formatted_frame = ttk.Frame(self.output_notebook, style='TFrame')

        # Search/Filter bar
        search_frame = ttk.Frame(formatted_frame, style='TFrame')
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Filter:", style='TLabel').pack(side=tk.LEFT, padx=(5, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_tree())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30, style='TEntry')
        search_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(search_frame, text="Clear Filter", command=self.clear_filter, style='TButton').pack(side=tk.LEFT)

        # Treeview with scrollbars
        tree_container = ttk.Frame(formatted_frame, style='TFrame')
        tree_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        tree_scroll_y = ttk.Scrollbar(tree_container, orient="vertical")
        tree_scroll_x = ttk.Scrollbar(tree_container, orient="horizontal")

        self.tree = ttk.Treeview(tree_container,
            show='tree headings',
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            style='Treeview')

        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Enable column sorting
        self.tree.bind('<Button-1>', self.on_tree_click)
        self.sort_reverse = {}
        self.tree_data = []  # Store original data for filtering

        self.output_notebook.add(formatted_frame, text="Formatted Output")

        # Raw Output Tab
        raw_frame = ttk.Frame(self.output_notebook, style='TFrame')

        self.raw_output = scrolledtext.ScrolledText(
            raw_frame,
            wrap=tk.WORD,
            bg=self.bg_grey_medium,
            fg=self.text_white,
            insertbackground=self.text_white,
            font=('Consolas', 9),
            padx=10,
            pady=10,
            relief=tk.FLAT)
        self.raw_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.output_notebook.add(raw_frame, text="Raw Output")

        # --- Status Bar ---
        status_frame = tk.Frame(root, bg=self.maroon, height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        self.status = tk.Label(
            status_frame,
            text="Ready",
            anchor=tk.W,
            bg=self.maroon,
            fg=self.text_white,
            font=('Segoe UI', 9),
            padx=10)
        self.status.pack(fill=tk.BOTH, expand=True)

    def make_request(self, endpoint, method="GET", params=None, data=None, stream=False):
        """Make HTTP request to Qualys API"""
        try:
            url = f"{self.api_url.get()}{endpoint}"
            auth = HTTPBasicAuth(self.username.get(), self.password.get())
            headers = {"X-Requested-With": "QuAPI Python Client"}

            self.status.config(text=f"Sending {method} request to {endpoint}...")
            self.root.update()

            response = requests.request(
                method,
                url,
                auth=auth,
                headers=headers,
                params=params,
                data=data,
                stream=stream,
                timeout=30)

            self.status.config(text=f"Response: {response.status_code} - {response.reason}")
            return response

        except requests.exceptions.Timeout:
            self.status.config(text="Error: Request timed out")
            messagebox.showerror("Timeout Error", "The request timed out. Please try again.")
            return None
        except requests.exceptions.ConnectionError:
            self.status.config(text="Error: Connection failed")
            messagebox.showerror("Connection Error", "Could not connect to the API. Check your URL and network.")
            return None
        except Exception as e:
            self.status.config(text=f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            return None

    def display_in_tree(self, columns, data, clear=True):
        """Display data in treeview with sortable columns"""
        if clear:
            self.tree.delete(*self.tree.get_children())
            self.sort_reverse = {}

        self.tree["columns"] = columns
        self.tree["show"] = "headings"
        self.tree_data = data  # Store for filtering

        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_tree_column(c))
            self.tree.column(col, width=150, anchor=tk.W, minwidth=100)
            self.sort_reverse[col] = False

        for row in data:
            self.tree.insert("", "end", values=row)

        # Switch to formatted output tab
        self.output_notebook.select(0)

    def filter_tree(self):
        """Filter tree view based on search term"""
        search_term = self.search_var.get().lower()

        # Clear current tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Re-populate with filtered data
        if not search_term:
            # Show all data if no search term
            for row in self.tree_data:
                self.tree.insert("", "end", values=row)
        else:
            # Filter data
            for row in self.tree_data:
                # Check if search term is in any column
                if any(search_term in str(cell).lower() for cell in row):
                    self.tree.insert("", "end", values=row)

    def clear_filter(self):
        """Clear the filter search box"""
        self.search_var.set("")

    def sort_tree_column(self, col):
        """Sort treeview by column"""
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]

        # Try to sort as numbers first, fall back to strings
        try:
            items.sort(key=lambda x: float(x[0]) if x[0] else 0, reverse=self.sort_reverse[col])
        except (ValueError, TypeError):
            items.sort(key=lambda x: x[0].lower() if x[0] else '', reverse=self.sort_reverse[col])

        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)

        self.sort_reverse[col] = not self.sort_reverse[col]

    def on_tree_click(self, event):
        """Handle tree click events"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            return "break"

    def display_raw_output(self, response):
        """Display raw API response"""
        if response is None:
            self.raw_output.delete("1.0", tk.END)
            self.raw_output.insert(tk.END, "No response received.\n")
            return

        header = f"Status Code: {response.status_code} {response.reason}\n"
        header += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"URL: {response.url}\n"
        header += "-" * 80 + "\n\n"

        content = ""
        try:
            # Try parsing as XML
            root = ET.fromstring(response.text)
            content = self.prettify_xml(root)
        except:
            try:
                # Try parsing as JSON
                content = json.dumps(response.json(), indent=2)
            except:
                # Plain text
                content = response.text

        self.raw_output.delete("1.0", tk.END)
        self.raw_output.insert(tk.END, header + content)

        # Switch to raw output tab
        self.output_notebook.select(1)

    def display_both_outputs(self, response, parser_func, columns):
        """Display both formatted and raw output"""
        if response is None or response.status_code != 200:
            error_msg = f"API request failed.\nStatus: {response.status_code if response else 'N/A'}\n"
            if response:
                error_msg += f"\n{response.text[:500]}"
            messagebox.showerror("API Error", error_msg)
            if response:
                self.display_raw_output(response)
            return

        try:
            # Parse and display formatted output
            root = ET.fromstring(response.text)
            data = parser_func(root)
            self.display_in_tree(columns, data)

            # Also update raw output
            self.display_raw_output(response)

        except Exception as e:
            messagebox.showerror("Parse Error", f"Could not parse response:\n{str(e)}")
            self.display_raw_output(response)

    def prettify_xml(self, elem, level=0):
        """Pretty print XML"""
        indent = "  " * level
        result = f"{indent}<{elem.tag}"

        # Add attributes
        if elem.attrib:
            for key, val in elem.attrib.items():
                result += f' {key}="{val}"'
        result += ">\n"

        # Add text
        if elem.text and elem.text.strip():
            result += f"{indent}  {elem.text.strip()}\n"

        # Add children
        for child in elem:
            result += self.prettify_xml(child, level + 1)

        result += f"{indent}</{elem.tag}>\n"
        return result

    # ==================== PARSERS ====================

    def parse_list_reports(self, root):
        """Parse report list XML"""
        reports = []
        for r in root.findall('.//REPORT'):
            report_id = self.get_xml_text(r, 'ID', 'N/A')
            title = self.get_xml_text(r, 'TITLE', 'N/A')
            status = self.get_xml_text(r, 'STATUS/STATE', 'N/A')
            output_format = self.get_xml_text(r, 'OUTPUT_FORMAT', 'N/A')
            launch_time = self.get_xml_text(r, 'LAUNCH_DATETIME', 'N/A')
            reports.append((report_id, title, status, output_format, launch_time))
        return reports

    def parse_list_scans(self, root):
        """Parse scan list XML"""
        scans = []
        for s in root.findall('.//SCAN'):
            ref = self.get_xml_text(s, 'REF', 'N/A')
            title = self.get_xml_text(s, 'TITLE', 'N/A')
            status = self.get_xml_text(s, 'STATUS/STATE', 'N/A')
            target = self.get_xml_text(s, 'TARGET', 'N/A')
            launch_time = self.get_xml_text(s, 'LAUNCH_DATETIME', 'N/A')
            self.scan_refs[title] = ref
            scans.append((ref, title, status, target, launch_time))
        return scans

    def parse_list_agents(self, root):
        """Parse agent list XML"""
        agents = []
        for a in root.findall('.//ServiceResponse/data'):
            agent_id = self.get_xml_text(a, 'agentId', 'N/A')
            name = self.get_xml_text(a, 'name', 'N/A')
            status = self.get_xml_text(a, 'status', 'N/A')
            version = self.get_xml_text(a, 'agentVersion', 'N/A')
            last_checkin = self.get_xml_text(a, 'lastCheckedInDate', 'N/A')
            agents.append((agent_id, name, status, version, last_checkin))
        return agents

    def parse_list_report_templates(self, root):
        """Parse report template list XML"""
        templates = []
        self.report_templates.clear()
        for t in root.findall('.//REPORT_TEMPLATE'):
            template_id = self.get_xml_text(t, 'ID', 'N/A')
            title = self.get_xml_text(t, 'TITLE', 'N/A')
            template_type = self.get_xml_text(t, 'TYPE', 'N/A')
            templates.append((template_id, title, template_type))
            self.report_templates[title] = template_id
        return templates

    def parse_list_host_assets(self, root):
        """Parse host asset list XML"""
        hosts = []
        for h in root.findall('.//HOST'):
            ip = self.get_xml_text(h, 'IP', 'N/A')
            dns = self.get_xml_text(h, 'DNS', 'N/A')
            netbios = self.get_xml_text(h, 'NETBIOS', 'N/A')
            os = self.get_xml_text(h, 'OS', 'N/A')
            tracking = self.get_xml_text(h, 'TRACKING_METHOD', 'N/A')
            # Only add if we have at least one value
            if ip != 'N/A' or dns != 'N/A' or netbios != 'N/A':
                hosts.append((ip, dns, netbios, os, tracking))
        return hosts

    def parse_scan_targets(self, root):
        """Parse scan target list XML"""
        targets = []
        for t in root.findall('.//SCAN_TARGET'):
            target_id = self.get_xml_text(t, 'ID', 'N/A')
            title = self.get_xml_text(t, 'TITLE', 'N/A')
            hosts = self.get_xml_text(t, 'HOSTS', 'N/A')
            targets.append((target_id, title, hosts))
        return targets

    def parse_vulnerabilities(self, root):
        """Parse vulnerability KB list XML"""
        vulns = []
        for v in root.findall('.//VULN'):
            qid = self.get_xml_text(v, 'QID', 'N/A')
            title = self.get_xml_text(v, 'TITLE', 'N/A')
            severity = self.get_xml_text(v, 'SEVERITY_LEVEL', 'N/A')
            vuln_type = self.get_xml_text(v, 'VULN_TYPE', 'N/A')
            published = self.get_xml_text(v, 'PUBLISHED_DATETIME', 'N/A')
            vulns.append((qid, title, severity, vuln_type, published))
        return vulns

    def parse_host_details(self, root):
        """Parse host details XML"""
        hosts = []
        for h in root.findall('.//HOST'):
            ip = self.get_xml_text(h, 'IP', 'N/A')
            dns = self.get_xml_text(h, 'DNS', 'N/A')
            netbios = self.get_xml_text(h, 'NETBIOS', 'N/A')
            os = self.get_xml_text(h, 'OS', 'N/A')
            tracking = self.get_xml_text(h, 'TRACKING_METHOD', 'N/A')
            last_scan = self.get_xml_text(h, 'LAST_SCAN_DATETIME', 'N/A')
            hosts.append((ip, dns, netbios, os, tracking, last_scan))
        return hosts

    def get_xml_text(self, element, path, default=''):
        """Safely extract text from XML element"""
        try:
            found = element.find(path)
            return found.text if found is not None and found.text else default
        except:
            return default

    # ==================== API OPERATIONS ====================

    def list_reports(self):
        """List all reports"""
        response = self.make_request("/api/2.0/fo/report/", params={"action": "list"})
        self.display_both_outputs(response, self.parse_list_reports,
            ["ID", "Title", "Status", "Format", "Launch Time"])

    def list_scans(self):
        """List all scans"""
        response = self.make_request("/api/2.0/fo/scan/", params={"action": "list"})
        self.display_both_outputs(response, self.parse_list_scans,
            ["Reference", "Title", "Status", "Target", "Launch Time"])

    def list_agents(self):
        """List cloud agents"""
        # Try multiple endpoints as Qualys API varies by platform
        response = self.make_request("/api/2.0/fo/asset/host/",
            params={"action": "list", "details": "Basic", "truncation_limit": "100"})

        if response:
            self.display_raw_output(response)
            if response.status_code == 404:
                messagebox.showinfo("Alternative Endpoint",
                    "Cloud agents endpoint may vary by platform.\nTry: Asset Management > Search Assets\nOr use Custom Request to test:\n/qps/rest/2.0/count/am/hostasset")

    def list_activation_keys(self):
        """List activation keys for cloud agents"""
        response = self.make_request("/qps/rest/2.0/get/am/key",
            params={"details": "All"})

        if response:
            self.display_raw_output(response)
            if response.status_code == 404:
                messagebox.showinfo("Alternative Endpoint",
                    "Try using Custom Request with:\nGET /qps/rest/2.0/get/am/key\nOr check your API permissions.")

    def list_report_templates(self):
        """List report templates"""
        # Try POST method first as some Qualys APIs require it
        response = self.make_request("/api/2.0/fo/report/",
            method="POST",
            data={"action": "list", "type": "template"})

        if response and response.status_code == 200:
            try:
                root = ET.fromstring(response.text)
                data = self.parse_list_report_templates(root)
                if data:
                    self.display_in_tree(["ID", "Title", "Type"], data)
                    self.display_raw_output(response)
                    messagebox.showinfo("Success", f"Fetched {len(self.report_templates)} report templates.")
                else:
                    self.display_raw_output(response)
                    messagebox.showwarning("No Templates", "No report templates found in response.")
            except Exception as e:
                messagebox.showerror("Parse Error", f"Could not parse response:\n{str(e)}")
                self.display_raw_output(response)
        else:
            if response:
                self.display_raw_output(response)
                messagebox.showerror("API Error",
                    f"Failed to fetch templates.\nStatus: {response.status_code}\nTry using Custom Request to test different endpoints.")

    def list_scan_targets(self):
        """List scan targets"""
        response = self.make_request("/api/2.0/fo/asset/ip/", params={"action": "list"})
        if response:
            self.display_raw_output(response)

    def search_assets(self):
        """Search for assets by IP, DNS, or NetBIOS"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Search Assets")
        dialog.configure(bg=self.bg_grey_dark)
        dialog.geometry("500x250")
        dialog.resizable(False, False)

        main_frame = ttk.Frame(dialog, style='Card.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(main_frame, text="Search By:", style='Header.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10))

        search_type = tk.StringVar(value="ip")
        ttk.Radiobutton(main_frame, text="IP Address", variable=search_type,
            value="ip").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Radiobutton(main_frame, text="DNS Hostname", variable=search_type,
            value="dns").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Radiobutton(main_frame, text="NetBIOS Hostname", variable=search_type,
            value="netbios").grid(row=3, column=0, sticky=tk.W, pady=2)

        ttk.Label(main_frame, text="Search Term:", style='TLabel').grid(
            row=4, column=0, sticky=tk.W, pady=(15, 5))
        search_entry = ttk.Entry(main_frame, width=40, style='TEntry')
        search_entry.grid(row=5, column=0, sticky=tk.EW, pady=(0, 15))
        search_entry.focus()

        def submit():
            term = search_entry.get().strip()
            if not term:
                messagebox.showwarning("Input Required", "Please enter a search term.")
                return

            params = {"action": "list"}

            search_by = search_type.get()
            if search_by == "ip":
                params["ips"] = term
            elif search_by == "dns":
                params["dns"] = term
            elif search_by == "netbios":
                params["netbios"] = term

            dialog.destroy()
            response = self.make_request("/api/2.0/fo/asset/host/", params=params)
            self.display_both_outputs(response, self.parse_list_host_assets,
                ["IP", "DNS", "NetBIOS", "OS", "Tracking Method"])

        button_frame = ttk.Frame(main_frame, style='Card.TFrame')
        button_frame.grid(row=6, column=0, pady=(10, 0))

        ttk.Button(button_frame, text="Search", command=submit, style='Action.TButton').pack(
            side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5)

        main_frame.columnconfigure(0, weight=1)
        dialog.bind('<Return>', lambda e: submit())

    def get_host_details(self):
        """Get detailed information about a specific host"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Get Host Details")
        dialog.configure(bg=self.bg_grey_dark)
        dialog.geometry("450x180")
        dialog.resizable(False, False)

        main_frame = ttk.Frame(dialog, style='Card.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(main_frame, text="Host IP Address:", style='TLabel').pack(
            anchor=tk.W, pady=(0, 5))
        ip_entry = ttk.Entry(main_frame, width=40, style='TEntry')
        ip_entry.pack(fill=tk.X, pady=(0, 20))
        ip_entry.focus()

        def submit():
            ip = ip_entry.get().strip()
            if not ip:
                messagebox.showwarning("Input Required", "Please enter an IP address.")
                return

            dialog.destroy()
            response = self.make_request("/api/2.0/fo/asset/host/",
                params={"action": "list", "details": "All", "ips": ip})
            self.display_both_outputs(response, self.parse_host_details,
                ["IP", "DNS", "NetBIOS", "OS", "Tracking", "Last Scan"])

        button_frame = ttk.Frame(main_frame, style='Card.TFrame')
        button_frame.pack()

        ttk.Button(button_frame, text="Get Details", command=submit,
            style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5)

        dialog.bind('<Return>', lambda e: submit())

    def launch_report(self):
        """Launch a new report"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Launch Report")
        dialog.configure(bg=self.bg_grey_dark)
        dialog.geometry("600x500")

        main_frame = ttk.Frame(dialog, style='Card.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Report Title
        ttk.Label(main_frame, text="Report Title:", style='TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=5)
        title_entry = ttk.Entry(main_frame, width=45, style='TEntry')
        title_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, pady=5, padx=(10, 0))
        title_entry.insert(0, f"Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        # Report Template
        ttk.Label(main_frame, text="Report Template:", style='TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=5)
        template_var = tk.StringVar()
        template_dropdown = ttk.Combobox(main_frame, textvariable=template_var,
            width=42, state='readonly')
        if self.report_templates:
            template_dropdown['values'] = list(self.report_templates.keys())
        template_dropdown.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(10, 5))

        def fetch_templates():
            self.list_report_templates()
            template_dropdown['values'] = list(self.report_templates.keys())
            if self.report_templates:
                template_dropdown.current(0)

        ttk.Button(main_frame, text="Fetch", command=fetch_templates).grid(
            row=1, column=2, padx=(5, 0))

        # Report Type
        ttk.Label(main_frame, text="Report Type:", style='TLabel').grid(
            row=2, column=0, sticky=tk.W, pady=5)
        type_var = tk.StringVar(value="Scan")
        type_dropdown = ttk.Combobox(main_frame, textvariable=type_var,
            values=["Scan", "Host"], width=42, state='readonly')
        type_dropdown.grid(row=2, column=1, columnspan=2, sticky=tk.EW, pady=5, padx=(10, 0))

        # Output Format
        ttk.Label(main_frame, text="Output Format:", style='TLabel').grid(
            row=3, column=0, sticky=tk.W, pady=5)
        format_var = tk.StringVar(value="csv")
        format_dropdown = ttk.Combobox(main_frame, textvariable=format_var,
            values=["csv", "pdf", "xml", "html"], width=42, state='readonly')
        format_dropdown.grid(row=3, column=1, columnspan=2, sticky=tk.EW, pady=5, padx=(10, 0))

        # Include Tags
        ttk.Label(main_frame, text="Include Tags (CSV):", style='TLabel').grid(
            row=4, column=0, sticky=tk.W, pady=5)
        include_tags_entry = ttk.Entry(main_frame, width=45, style='TEntry')
        include_tags_entry.grid(row=4, column=1, columnspan=2, sticky=tk.EW, pady=5, padx=(10, 0))

        # Exclude Tags
        ttk.Label(main_frame, text="Exclude Tags (CSV):", style='TLabel').grid(
            row=5, column=0, sticky=tk.W, pady=5)
        exclude_tags_entry = ttk.Entry(main_frame, width=45, style='TEntry')
        exclude_tags_entry.grid(row=5, column=1, columnspan=2, sticky=tk.EW, pady=5, padx=(10, 0))

        def submit():
            template_name = template_var.get()
            if not template_name or template_name not in self.report_templates:
                messagebox.showerror("Error", "Please select a valid report template.")
                return

            payload = {
                "action": "launch",
                "report_title": title_entry.get(),
                "template_id": self.report_templates[template_name],
                "report_type": type_var.get(),
                "output_format": format_var.get()
            }

            if include_tags_entry.get().strip():
                payload["tag_set_include"] = include_tags_entry.get().strip()
            if exclude_tags_entry.get().strip():
                payload["tag_set_exclude"] = exclude_tags_entry.get().strip()

            dialog.destroy()
            response = self.make_request("/api/2.0/fo/report/", method="POST", data=payload)
            self.display_raw_output(response)

            if response and response.status_code == 200:
                messagebox.showinfo("Success", "Report launched successfully!")

        button_frame = ttk.Frame(main_frame, style='Card.TFrame')
        button_frame.grid(row=6, column=0, columnspan=3, pady=(20, 0))

        ttk.Button(button_frame, text="Launch Report", command=submit,
            style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5)

        main_frame.columnconfigure(1, weight=1)

    def fetch_report(self):
        """Fetch/download a report by ID"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Fetch Report")
        dialog.configure(bg=self.bg_grey_dark)
        dialog.geometry("450x180")
        dialog.resizable(False, False)

        main_frame = ttk.Frame(dialog, style='Card.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(main_frame, text="Report ID:", style='TLabel').pack(
            anchor=tk.W, pady=(0, 5))
        id_entry = ttk.Entry(main_frame, width=40, style='TEntry')
        id_entry.pack(fill=tk.X, pady=(0, 20))
        id_entry.focus()

        def submit():
            report_id = id_entry.get().strip()
            if not report_id:
                messagebox.showwarning("Input Required", "Please enter a report ID.")
                return

            response = self.make_request("/api/2.0/fo/report/",
                params={"action": "fetch", "id": report_id})
            dialog.destroy()

            if response and response.status_code == 200:
                content_type = response.headers.get('content-type', 'text/plain')

                # Determine file extension
                if 'csv' in content_type:
                    ext = 'csv'
                elif 'pdf' in content_type:
                    ext = 'pdf'
                elif 'xml' in content_type:
                    ext = 'xml'
                elif 'html' in content_type:
                    ext = 'html'
                else:
                    ext = 'txt'

                filepath = filedialog.asksaveasfilename(
                    defaultextension=f".{ext}",
                    filetypes=[
                        ("CSV files", "*.csv"),
                        ("PDF files", "*.pdf"),
                        ("XML files", "*.xml"),
                        ("HTML files", "*.html"),
                        ("All files", "*.*")
                    ],
                    initialfile=f"report_{report_id}.{ext}"
                )

                if filepath:
                    mode = 'wb' if ext == 'pdf' else 'w'
                    encoding = None if ext == 'pdf' else 'utf-8'

                    with open(filepath, mode, encoding=encoding) as f:
                        if ext == 'pdf':
                            f.write(response.content)
                        else:
                            f.write(response.text)

                    self.status.config(text=f"Report saved to {filepath}")
                    messagebox.showinfo("Success", f"Report saved successfully to:\n{filepath}")
            else:
                self.display_raw_output(response)

        button_frame = ttk.Frame(main_frame, style='Card.TFrame')
        button_frame.pack()

        ttk.Button(button_frame, text="Fetch & Save", command=submit,
            style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5)

        dialog.bind('<Return>', lambda e: submit())

    def delete_report(self):
        """Delete a report by ID"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Delete Report")
        dialog.configure(bg=self.bg_grey_dark)
        dialog.geometry("450x180")
        dialog.resizable(False, False)

        main_frame = ttk.Frame(dialog, style='Card.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(main_frame, text="Report ID:", style='TLabel').pack(
            anchor=tk.W, pady=(0, 5))
        id_entry = ttk.Entry(main_frame, width=40, style='TEntry')
        id_entry.pack(fill=tk.X, pady=(0, 20))
        id_entry.focus()

        def submit():
            report_id = id_entry.get().strip()
            if not report_id:
                messagebox.showwarning("Input Required", "Please enter a report ID.")
                return

            confirm = messagebox.askyesno("Confirm Deletion",
                f"Are you sure you want to delete report ID {report_id}?")

            if confirm:
                response = self.make_request("/api/2.0/fo/report/",
                    method="POST",
                    data={"action": "delete", "id": report_id})
                dialog.destroy()
                self.display_raw_output(response)

                if response and response.status_code == 200:
                    messagebox.showinfo("Success", "Report deleted successfully!")

        button_frame = ttk.Frame(main_frame, style='Card.TFrame')
        button_frame.pack()

        ttk.Button(button_frame, text="Delete", command=submit,
            style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5)

        dialog.bind('<Return>', lambda e: submit())

    def launch_scan(self):
        """Launch a new scan"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Launch Scan")
        dialog.configure(bg=self.bg_grey_dark)
        dialog.geometry("600x450")

        main_frame = ttk.Frame(dialog, style='Card.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scan Title
        ttk.Label(main_frame, text="Scan Title:", style='TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=5)
        title_entry = ttk.Entry(main_frame, width=45, style='TEntry')
        title_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        title_entry.insert(0, f"Scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        # Scan Type
        ttk.Label(main_frame, text="Scan Type:", style='TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=5)
        scan_type_var = tk.StringVar(value="option_title")
        type_frame = ttk.Frame(main_frame, style='Card.TFrame')
        type_frame.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        ttk.Radiobutton(type_frame, text="Option Profile", variable=scan_type_var,
            value="option_title").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(type_frame, text="Scan Title", variable=scan_type_var,
            value="scan_title").pack(side=tk.LEFT)

        # Option Profile / Scan
        ttk.Label(main_frame, text="Option Profile:", style='TLabel').grid(
            row=2, column=0, sticky=tk.W, pady=5)
        option_entry = ttk.Entry(main_frame, width=45, style='TEntry')
        option_entry.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        option_entry.insert(0, "Initial Options")

        # Target IPs
        ttk.Label(main_frame, text="Target IPs:", style='TLabel').grid(
            row=3, column=0, sticky=tk.NW, pady=5)
        ip_text = scrolledtext.ScrolledText(main_frame, width=45, height=8,
            bg=self.bg_grey_light, fg=self.text_white, insertbackground=self.text_white,
            font=('Consolas', 9))
        ip_text.grid(row=3, column=1, sticky=tk.EW, pady=5, padx=(10, 0))

        def submit():
            scan_title = title_entry.get().strip()
            option_profile = option_entry.get().strip()
            target_ips = ip_text.get("1.0", tk.END).strip()

            if not scan_title or not target_ips:
                messagebox.showerror("Error", "Please provide scan title and target IPs.")
                return

            payload = {
                "action": "launch",
                "scan_title": scan_title,
                "ip": target_ips,
                scan_type_var.get(): option_profile
            }

            dialog.destroy()
            response = self.make_request("/api/2.0/fo/scan/", method="POST", data=payload)
            self.display_raw_output(response)

            if response and response.status_code == 200:
                messagebox.showinfo("Success", "Scan launched successfully!")

        button_frame = ttk.Frame(main_frame, style='Card.TFrame')
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(button_frame, text="Launch Scan", command=submit,
            style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5)

        main_frame.columnconfigure(1, weight=1)

    def get_scan_results(self):
        """Get scan results by scan reference"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Get Scan Results")
        dialog.configure(bg=self.bg_grey_dark)
        dialog.geometry("450x180")
        dialog.resizable(False, False)

        main_frame = ttk.Frame(dialog, style='Card.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(main_frame, text="Scan Reference:", style='TLabel').pack(
            anchor=tk.W, pady=(0, 5))
        ref_entry = ttk.Entry(main_frame, width=40, style='TEntry')
        ref_entry.pack(fill=tk.X, pady=(0, 20))
        ref_entry.focus()

        def submit():
            scan_ref = ref_entry.get().strip()
            if not scan_ref:
                messagebox.showwarning("Input Required", "Please enter a scan reference.")
                return

            dialog.destroy()
            response = self.make_request("/api/2.0/fo/scan/",
                params={"action": "fetch", "scan_ref": scan_ref, "mode": "extended"})
            self.display_raw_output(response)

        button_frame = ttk.Frame(main_frame, style='Card.TFrame')
        button_frame.pack()

        ttk.Button(button_frame, text="Get Results", command=submit,
            style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5)

        dialog.bind('<Return>', lambda e: submit())

    def search_vulnerabilities(self):
        """Search Knowledge Base for vulnerabilities"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Search Vulnerabilities")
        dialog.configure(bg=self.bg_grey_dark)
        dialog.geometry("500x280")

        main_frame = ttk.Frame(dialog, style='Card.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(main_frame, text="Search Term (QID or keyword):", style='TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=5)
        search_entry = ttk.Entry(main_frame, width=40, style='TEntry')
        search_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        search_entry.focus()

        ttk.Label(main_frame, text="Severity Level:", style='TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=5)
        severity_var = tk.StringVar(value="")
        severity_dropdown = ttk.Combobox(main_frame, textvariable=severity_var,
            values=["", "1", "2", "3", "4", "5"], width=37, state='readonly')
        severity_dropdown.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="Last Modified (days ago):", style='TLabel').grid(
            row=2, column=0, sticky=tk.W, pady=5)
        days_entry = ttk.Entry(main_frame, width=40, style='TEntry')
        days_entry.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=(10, 0))

        def submit():
            params = {"action": "list"}

            search_term = search_entry.get().strip()
            if search_term:
                params["details"] = "All"
                params["ids"] = search_term

            severity = severity_var.get()
            if severity:
                params["severities"] = severity

            days = days_entry.get().strip()
            if days:
                params["last_modified_after"] = days

            dialog.destroy()
            response = self.make_request("/api/2.0/fo/knowledge_base/vuln/", params=params)
            self.display_both_outputs(response, self.parse_vulnerabilities,
                ["QID", "Title", "Severity", "Type", "Published"])

        button_frame = ttk.Frame(main_frame, style='Card.TFrame')
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(button_frame, text="Search", command=submit,
            style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5)

        main_frame.columnconfigure(1, weight=1)
        dialog.bind('<Return>', lambda e: submit())

    def get_qid_details(self):
        """Get detailed information about a specific QID"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Get QID Details")
        dialog.configure(bg=self.bg_grey_dark)
        dialog.geometry("450x180")
        dialog.resizable(False, False)

        main_frame = ttk.Frame(dialog, style='Card.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(main_frame, text="QID (Vulnerability ID):", style='TLabel').pack(
            anchor=tk.W, pady=(0, 5))
        qid_entry = ttk.Entry(main_frame, width=40, style='TEntry')
        qid_entry.pack(fill=tk.X, pady=(0, 20))
        qid_entry.focus()

        def submit():
            qid = qid_entry.get().strip()
            if not qid:
                messagebox.showwarning("Input Required", "Please enter a QID.")
                return

            dialog.destroy()
            response = self.make_request("/api/2.0/fo/knowledge_base/vuln/",
                params={"action": "list", "details": "All", "ids": qid})
            self.display_raw_output(response)

        button_frame = ttk.Frame(main_frame, style='Card.TFrame')
        button_frame.pack()

        ttk.Button(button_frame, text="Get Details", command=submit,
            style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5)

        dialog.bind('<Return>', lambda e: submit())

    def get_user_info(self):
        """Get user information"""
        response = self.make_request("/api/2.0/fo/user/", params={"action": "list"})
        self.display_raw_output(response)

    def custom_request(self):
        """Make custom API request"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Custom API Request")
        dialog.configure(bg=self.bg_grey_dark)
        dialog.geometry("750x600")

        main_frame = ttk.Frame(dialog, style='Card.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Method
        ttk.Label(main_frame, text="Method:", style='TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=5)
        method_var = tk.StringVar(value="GET")
        method_dropdown = ttk.Combobox(main_frame, textvariable=method_var,
            values=["GET", "POST", "PUT", "DELETE"], width=15, state='readonly')
        method_dropdown.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # Endpoint
        ttk.Label(main_frame, text="Endpoint:", style='TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=5)
        endpoint_entry = ttk.Entry(main_frame, width=60, style='TEntry')
        endpoint_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        endpoint_entry.insert(0, "/api/2.0/fo/user/")

        # Parameters
        ttk.Label(main_frame, text="Parameters:", style='TLabel').grid(
            row=2, column=0, sticky=tk.NW, pady=5)
        params_text = scrolledtext.ScrolledText(main_frame, width=60, height=6,
            bg=self.bg_grey_light, fg=self.text_white, insertbackground=self.text_white,
            font=('Consolas', 9))
        params_text.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        params_text.insert("1.0", "# One per line: key=value\naction=list")

        # Data/Body
        ttk.Label(main_frame, text="Body:", style='TLabel').grid(
            row=3, column=0, sticky=tk.NW, pady=5)
        data_text = scrolledtext.ScrolledText(main_frame, width=60, height=6,
            bg=self.bg_grey_light, fg=self.text_white, insertbackground=self.text_white,
            font=('Consolas', 9))
        data_text.grid(row=3, column=1, sticky=tk.EW, pady=5, padx=(10, 0))

        # Example section
        ttk.Label(main_frame, text="Examples:", style='Header.TLabel').grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=(15, 5))

        examples_frame = ttk.Frame(main_frame, style='Card.TFrame')
        examples_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))

        def load_example_1():
            endpoint_entry.delete(0, tk.END)
            endpoint_entry.insert(0, "/api/2.0/fo/user/")
            params_text.delete("1.0", tk.END)
            params_text.insert("1.0", "action=list")
            data_text.delete("1.0", tk.END)
            method_var.set("GET")

        def load_example_2():
            endpoint_entry.delete(0, tk.END)
            endpoint_entry.insert(0, "/api/2.0/fo/report/")
            params_text.delete("1.0", tk.END)
            data_text.delete("1.0", tk.END)
            data_text.insert("1.0", "action=list")
            method_var.set("POST")

        def load_example_3():
            endpoint_entry.delete(0, tk.END)
            endpoint_entry.insert(0, "/api/2.0/fo/scan/")
            params_text.delete("1.0", tk.END)
            params_text.insert("1.0", "action=list")
            data_text.delete("1.0", tk.END)
            method_var.set("GET")

        ttk.Button(examples_frame, text="Ex 1: List Users (GET)",
            command=load_example_1).pack(side=tk.LEFT, padx=5)
        ttk.Button(examples_frame, text="Ex 2: List Reports (POST)",
            command=load_example_2).pack(side=tk.LEFT, padx=5)
        ttk.Button(examples_frame, text="Ex 3: List Scans (GET)",
            command=load_example_3).pack(side=tk.LEFT, padx=5)

        def submit():
            endpoint = endpoint_entry.get().strip()
            if not endpoint:
                messagebox.showerror("Error", "Please provide an endpoint.")
                return

            # Parse parameters
            params = {}
            params_raw = params_text.get("1.0", tk.END).strip()
            for line in params_raw.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, val = line.split('=', 1)
                        params[key.strip()] = val.strip()

            # Get body data
            data = data_text.get("1.0", tk.END).strip()
            if not data:
                data = None

            dialog.destroy()
            response = self.make_request(
                endpoint,
                method=method_var.get(),
                params=params if params else None,
                data=data
            )
            self.display_raw_output(response)

        button_frame = ttk.Frame(main_frame, style='Card.TFrame')
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(button_frame, text="Send Request", command=submit,
            style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5)

        main_frame.columnconfigure(1, weight=1)

    def clear_output(self):
        """Clear all output"""
        self.tree.delete(*self.tree.get_children())
        self.raw_output.delete("1.0", tk.END)
        self.status.config(text="Output cleared")


# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    root = tk.Tk()
    app = QualysAPIClient(root)
    root.mainloop()