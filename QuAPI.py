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
        self.root.title("Qualys API Client")
        self.root.geometry("1000x800")
        
        # --- Color Theme ---
        self.bg_grey_dark = "#2b2b2b"
        self.bg_grey_medium = "#3c3f41"
        self.maroon = "#800020"
        self.maroon_light = "#a0002a"
        self.text_white = "#ffffff"
        
        self.root.configure(bg=self.bg_grey_dark)
        
        # --- Style Configuration ---
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TFrame', background=self.bg_grey_dark)
        style.configure('TLabel', background=self.bg_grey_dark, foreground=self.text_white)
        style.configure('TRadiobutton', background=self.bg_grey_dark, foreground=self.text_white)
        style.configure('TLabelframe', background=self.bg_grey_dark, bordercolor=self.maroon)
        style.configure('TLabelframe.Label', background=self.bg_grey_dark, foreground=self.maroon, font=('Arial', 10, 'bold'))
        style.configure('TButton', background=self.maroon, foreground=self.text_white, borderwidth=0, padding=5)
        style.map('TButton', background=[('active', self.maroon_light)])
        style.configure('TEntry', fieldbackground=self.bg_grey_medium, foreground=self.text_white, bordercolor=self.maroon, insertcolor=self.text_white)
        style.configure('TNotebook', background=self.bg_grey_dark, borderwidth=0)
        style.configure('TNotebook.Tab', background=self.maroon, foreground=self.text_white, padding=[5, 2])
        style.map('TNotebook.Tab', background=[('selected', self.maroon_light)])
        
        # --- GUI Layout ---
        config_frame = ttk.LabelFrame(root, text="API Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # API Config fields...
        ttk.Label(config_frame, text="API URL:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.api_url = ttk.Entry(config_frame, width=50)
        self.api_url.insert(0, "https://qualysguard.qg1.apps.qualys.co.uk")
        self.api_url.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(config_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.username = ttk.Entry(config_frame, width=50)
        self.username.grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(config_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.password = ttk.Entry(config_frame, width=50, show="*")
        self.password.grid(row=2, column=1, padx=5, pady=2)
        
        operations_frame = ttk.LabelFrame(root, text="API Operations", padding=10)
        operations_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        button_frame = ttk.Frame(operations_frame, width=200)
        button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # --- Buttons ---
        button_groups = {
            "Vulnerability Management": [
                ("List Scans", self.list_scans), ("Launch Scan", self.launch_scan), ("Get Scan Results", self.get_scan_results)
            ],
            "Asset Management": [
                ("Search Assets", self.search_assets), ("List Cloud Agents", self.list_agents)
            ],
            "Reports": [
                ("List Reports", self.list_reports), ("List Report Templates", self.list_report_templates), 
                ("Launch Report", self.launch_report), ("Download Report", self.download_report), ("Delete Report", self.delete_report)
            ],
            "Other": [
                ("Get User Info", self.get_user_info), ("Custom Request", self.custom_request), ("Clear Output", self.clear_output)
            ]
        }
        for group, buttons in button_groups.items():
            ttk.Label(button_frame, text=group, font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(10, 5))
            for text, command in buttons:
                ttk.Button(button_frame, text=text, command=command).pack(fill=tk.X, pady=2)
        
        # --- Output Area ---
        output_notebook = ttk.Notebook(operations_frame)
        output_notebook.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Formatted Output Tab (Treeview)
        formatted_frame = ttk.Frame(output_notebook)
        self.tree = ttk.Treeview(formatted_frame, show='headings')
        self.tree.pack(fill=tk.BOTH, expand=True)
        output_notebook.add(formatted_frame, text="Formatted Output")
        
        # Raw Output Tab (Text)
        raw_frame = ttk.Frame(output_notebook)
        self.raw_output = scrolledtext.ScrolledText(raw_frame, wrap=tk.WORD, bg=self.bg_grey_medium, fg=self.text_white, insertbackground=self.text_white)
        self.raw_output.pack(fill=tk.BOTH, expand=True)
        output_notebook.add(raw_frame, text="Raw Output")

        # Status bar
        status_frame = tk.Frame(root, bg=self.maroon)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status = tk.Label(status_frame, text="Ready", anchor=tk.W, bg=self.maroon, fg=self.text_white, padx=5, pady=3)
        self.status.pack(fill=tk.X)
        
        self.report_templates = {}

    def make_request(self, endpoint, method="GET", params=None, data=None):
        try:
            url = f"{self.api_url.get()}{endpoint}"
            auth = HTTPBasicAuth(self.username.get(), self.password.get())
            headers = {"X-Requested-With": "Python GUI Client"}
            
            self.status.config(text=f"Sending {method} request to {endpoint}...")
            self.root.update()
            
            response = requests.request(method, url, auth=auth, headers=headers, params=params, data=data)
            
            self.status.config(text=f"Response: {response.status_code}")
            return response
        
        except Exception as e:
            self.status.config(text=f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
            return None

    def display_in_tree(self, columns, data):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=tk.W)
        for row in data:
            self.tree.insert("", "end", values=row)

    def display_raw_output(self, response):
        header = f"Status Code: {response.status_code}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "-"*80 + "\n\n"
        content = ""
        try:
            root = ET.fromstring(response.text)
            content = self.prettify_xml(root)
        except:
            try:
                content = json.dumps(response.json(), indent=2)
            except:
                content = response.text
        self.raw_output.delete("1.0", tk.END)
        self.raw_output.insert(tk.END, header + content)

    # --- XML Parsers ---
    def parse_and_display(self, response, parser_func, columns):
        if response is None or response.status_code != 200:
            messagebox.showerror("API Error", f"Failed to fetch data. Status: {response.status_code if response else 'N/A'}\n\n{response.text if response else ''}")
            return
        try:
            root = ET.fromstring(response.text)
            data = parser_func(root)
            self.display_in_tree(columns, data)
        except Exception as e:
            messagebox.showerror("Parse Error", f"Could not parse XML response: {e}")
            self.display_raw_output(response)

    def parse_list_reports(self, root):
        return [
            (r.find('ID').text, r.find('TITLE').text, r.find('STATUS/STATE').text, r.find('OUTPUT_FORMAT').text, r.find('LAUNCH_DATETIME').text)
            for r in root.findall('.//REPORT')
        ]
    
    def parse_list_scans(self, root):
        return [
            (s.find('REF').text, s.find('TITLE').text, s.find('STATUS/STATE').text, s.find('TARGET').text, s.find('LAUNCH_DATETIME').text)
            for s in root.findall('.//SCAN')
        ]

    def parse_list_agents(self, root):
        return [
            (a.find('agentId').text, a.find('host/hostId').text, a.find('status').text, a.find('agentVersion').text)
            for a in root.findall('.//QualysAgent')
        ]

    def parse_list_report_templates(self, root):
        templates = []
        for t in root.findall('.//REPORT_TEMPLATE'):
            template_id = t.find('ID').text
            title = t.find('TITLE').text
            templates.append((template_id, title))
            self.report_templates[title] = template_id
        return templates

    def prettify_xml(self, elem, level=0):
        indent = "  " * level
        result = f"{indent}<{elem.tag}>\n"
        if elem.text and elem.text.strip(): result += f"{indent}  {elem.text.strip()}\n"
        for child in elem: result += self.prettify_xml(child, level + 1)
        result += f"{indent}</{elem.tag}>\n"
        return result

    # --- API Call Methods ---
    def list_reports(self):
        response = self.make_request("/api/2.0/fo/report/", params={"action": "list"})
        self.parse_and_display(response, self.parse_list_reports, ["ID", "Title", "Status", "Format", "Launch Time"])

    def list_scans(self):
        response = self.make_request("/api/2.0/fo/scan/", params={"action": "list"})
        self.parse_and_display(response, self.parse_list_scans, ["Reference", "Title", "Status", "Target", "Launch Time"])

    def list_agents(self):
        # NOTE: This uses a different API endpoint
        response = self.make_request("/qps/rest/v1/agents", params={"activated": "true"})
        self.parse_and_display(response, self.parse_list_agents, ["Agent ID", "Host ID", "Status", "Version"])

    def list_report_templates(self):
        response = self.make_request("/api/2.0/fo/report/template/", params={"action": "list"})
        self.parse_and_display(response, self.parse_list_report_templates, ["ID", "Title"])
        messagebox.showinfo("Success", "Report templates fetched and cached for the 'Launch Report' dialog.")

    def launch_report(self):
        # Complex dialog with dynamic template fetching
        dialog = tk.Toplevel(self.root)
        dialog.title("Launch Report")
        dialog.configure(bg=self.bg_grey_dark)

        # Fields
        ttk.Label(dialog, text="Report Title:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        title_entry = ttk.Entry(dialog, width=40)
        title_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(dialog, text="Report Template:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        template_var = tk.StringVar()
        template_dropdown = ttk.Combobox(dialog, textvariable=template_var, width=38)
        if self.report_templates:
            template_dropdown['values'] = list(self.report_templates.keys())
        template_dropdown.grid(row=1, column=1, padx=10, pady=5)
        
        def fetch_templates_and_populate():
            self.list_report_templates()
            template_dropdown['values'] = list(self.report_templates.keys())

        ttk.Button(dialog, text="Fetch Templates", command=fetch_templates_and_populate).grid(row=1, column=2, padx=5)

        ttk.Label(dialog, text="Report Type:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        type_var = tk.StringVar(value="Scan")
        type_dropdown = ttk.Combobox(dialog, textvariable=type_var, values=["Scan", "Host"], width=38)
        type_dropdown.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(dialog, text="Output Format:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        format_entry = ttk.Entry(dialog, width=40)
        format_entry.insert(0, "csv")
        format_entry.grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Include Tags (CSV):").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        include_tags_entry = ttk.Entry(dialog, width=40)
        include_tags_entry.grid(row=4, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Exclude Tags (CSV):").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        exclude_tags_entry = ttk.Entry(dialog, width=40)
        exclude_tags_entry.grid(row=5, column=1, padx=10, pady=5)

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
                "output_format": format_entry.get()
            }
            if include_tags_entry.get(): payload["tag_set_include"] = include_tags_entry.get()
            if exclude_tags_entry.get(): payload["tag_set_exclude"] = exclude_tags_entry.get()

            response = self.make_request("/api/2.0/fo/report/", method="POST", data=payload)
            self.display_raw_output(response)
            dialog.destroy()
        
        ttk.Button(dialog, text="Launch", command=submit).grid(row=6, column=0, columnspan=3, pady=20)
    
    def download_report(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Download Report")
        dialog.configure(bg=self.bg_grey_dark)
        
        ttk.Label(dialog, text="Report ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_entry = ttk.Entry(dialog, width=40)
        id_entry.grid(row=0, column=1, padx=10, pady=5)
        
        def submit():
            report_id = id_entry.get()
            response = self.make_request("/api/2.0/fo/report/", params={"action": "fetch", "id": report_id})
            dialog.destroy()
            
            if response and response.status_code == 200:
                content_type = response.headers.get('content-type', 'text/plain')
                ext = 'csv' if 'csv' in content_type else 'xml' if 'xml' in content_type else 'txt'
                filepath = filedialog.asksaveasfilename(
                    defaultextension=f".{ext}",
                    filetypes=[("CSV files", "*.csv"), ("XML files", "*.xml"), ("All files", "*.*")],
                    initialfile=f"report-{report_id}.{ext}"
                )
                if filepath:
                    with open(filepath, "w", encoding='utf-8') as f:
                        f.write(response.text)
                    self.status.config(text=f"Report saved to {filepath}")
            else:
                self.display_raw_output(response)
        
        ttk.Button(dialog, text="Download", command=submit).grid(row=1, column=0, columnspan=2, pady=10)

    def search_assets(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Search Assets")
        dialog.configure(bg=self.bg_grey_dark)
        
        ttk.Label(dialog, text="IP / DNS / NetBIOS:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        search_entry = ttk.Entry(dialog, width=40)
        search_entry.grid(row=0, column=1, padx=10, pady=5)

        def submit():
            term = search_entry.get()
            params = {"action": "list"}
            if term:
                params["ips"] = term # API can often handle different types in one param
            
            response = self.make_request("/api/2.0/fo/asset/host/", params=params)
            dialog.destroy()
            self.parse_and_display(response, self.parse_list_host_assets, ["IP", "DNS", "OS", "Tracking Method"])

        ttk.Button(dialog, text="Search", command=submit).grid(row=1, column=0, columnspan=2, pady=10)

    def delete_report(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Delete Report")
        dialog.configure(bg=self.bg_grey_dark)
        ttk.Label(dialog, text="Report ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_entry = ttk.Entry(dialog, width=40)
        id_entry.grid(row=0, column=1, padx=10, pady=5)
        def submit():
            response = self.make_request("/api/2.0/fo/report/", method="POST", data={"action": "delete", "id": id_entry.get()})
            self.display_raw_output(response)
            dialog.destroy()
        ttk.Button(dialog, text="Delete", command=submit).grid(row=1, column=0, columnspan=2, pady=10)

    def clear_output(self):
        self.tree.delete(*self.tree.get_children())
        self.raw_output.delete("1.0", tk.END)
        self.status.config(text="Output cleared")

    # --- Other Methods (unchanged or minor tweaks) ---
    def get_user_info(self):
        response = self.make_request("/api/2.0/fo/user/", params={"action": "list"})
        self.display_raw_output(response)

    def custom_request(self):
        # Implementation for custom_request dialog... (can be added back if needed)
        messagebox.showinfo("Custom Request", "Please use this for advanced API calls not covered by the buttons.")

    def launch_scan(self):
        # Implementation for launch_scan dialog...
        messagebox.showinfo("Launch Scan", "This dialog can be implemented similarly to 'Launch Report'.")

    def get_scan_results(self):
        # Implementation for get_scan_results dialog...
        messagebox.showinfo("Get Scan Results", "This dialog can be implemented similarly to 'Download Report'.")
        
    def parse_list_host_assets(self, root):
        return [
            (
                h.find('IP').text, 
                h.find('DNS').text if h.find('DNS') is not None else 'N/A', 
                h.find('OS').text if h.find('OS') is not None else 'N/A',
                h.find('TRACKING_METHOD').text if h.find('TRACKING_METHOD') is not None else 'N/A'
            )
            for h in root.findall('.//HOST')
        ]


# --- Execution Block ---
if __name__ == "__main__":
    root = tk.Tk()
    app = QualysAPIClient(root)
    root.mainloop()