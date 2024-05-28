import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import libvirt
import subprocess


def actualizar_lista_vms(info_vm, seleccionar_vm):
        conn = libvirt.open('qemu:///system')
        if conn is None:
            print('No se pudo conectar al hipervisor')
            return

        try:
            for widget in info_vm.winfo_children():
                widget.destroy()

            # Maquinas virtuales no activas
            for vm_name in conn.listDefinedDomains():
                # btn_vm = tk.Button(info_vm, text=vm_name, command=lambda name=vm_name: seleccionar_vm(name))
                # btn_vm = tk.Button(info_vm, text=vm_name)
                # btn_vm.pack(padx=5, pady=5, fill=tk.X)
                lbl_vm = tk.Label(info_vm, text=vm_name, bg="lightgrey", relief=tk.RAISED, bd=2, height=2)
                lbl_vm.pack(padx=5, pady=5, fill=tk.X)
                lbl_vm.bind("<Button-1>", lambda event, name=vm_name: seleccionar_vm(event, name))

            # Maquinas virtuales activas
            for vm_id in conn.listDomainsID():
                dom = conn.lookupByID(vm_id)
                # btn_vm = tk.Button(info_vm, text=dom.name(), command=lambda name=dom.name(): seleccionar_vm(name))
                # btn_vm = tk.Button(info_vm, text=dom.name())
                # btn_vm.pack(padx=5, pady=5, fill=tk.X)
                # lbl_vm = tk.Label(info_vm, text=dom.name(), bg="lightgreen")
                lbl_vm = tk.Label(info_vm, text=dom.name(), bg="lightgrey", relief=tk.RAISED, bd=2)
                lbl_vm.pack(padx=5, pady=5, fill=tk.X)
                lbl_vm.bind("<Button-1>", lambda event, name=dom.name(): seleccionar_vm(event, name))

        except Exception as e:
            print(f'Error al obtener la lista de máquinas virtuales: {e}')
        finally:
            conn.close()

def crear(ventana_principal, info_vm, seleccionar_vm):

    actualizar_lista_vms(info_vm, seleccionar_vm)

    def crear_maquina_virtual(nombre, memoria, cpu, almacenamiento, iso, info_vm):
        conn = libvirt.open('qemu:///system')
        if conn is None:
            print('No se pudo conectar al hipervisor')
            return

        try:

            subprocess.run(['qemu-img', 'create', '-f', 'qcow2', f'/home/nicole/Documentos/disco_{nombre}.qcow2', f'{almacenamiento}G'])

            xml = f'''
                <domain type='qemu'>
                    <name>{nombre}</name>
                    <memory unit='KiB'>{int(memoria) * 1024}</memory>
                    <vcpu placement='static'>{cpu}</vcpu>
                    <os>
                        <type arch='x86_64' machine='pc'>hvm</type>
                        <boot dev='cdrom'/>
                    </os>
                    <devices>
                        <disk type='file' device='cdrom'>
                            <driver name='qemu' type='raw'/>
                            <source file='{iso}'/>
                            <target dev='hdc' bus='ide'/>
                            <readonly/>
                        </disk>                        
                        <disk type='file' device='disk'>
                            <driver name='qemu' type='qcow2'/>
                            <source file='/home/nicole/Documentos/disco_{nombre}.qcow2'/>
                            <target dev='vdb' bus='virtio'/>
                        </disk>
                        <interface type='network'>
                            <source network='default'/>
                            <model type='virtio'/>
                        </interface>
                        <graphics type='spice' port='5900' autoport='yes'>
                            <listen type='none'/>
                            <image compression='off'/>
                        </graphics>
                        <video>
                            <model type='virtio' heads='1' primary='yes'/>
                        </video>
                    </devices>
                </domain>
            '''

            # vm = conn.defineXML(xml)
            vm = conn.createXML(xml, 0)
            if vm is None:
                print('Error al crear la máquina virtual')
            else:
                messagebox.showinfo("Información", 'Máquina virtual creada y definida con éxito')

        except Exception as e:
            messagebox.showerror("Error", f'Error al crear la máquina virtual: {e}')
        finally:
            conn.close()

        actualizar_lista_vms(info_vm, seleccionar_vm)

    def crear_vm():
        nombre = nombre_entry.get()
        memoria = memoria_entry.get()
        cpu = cpu_entry.get()
        almacenamiento = almacenamiento_entry.get()
        iso = iso_entry.get()
        crear_maquina_virtual(nombre, memoria, cpu, almacenamiento, iso, info_vm)
        v_creacion.destroy()

    ancho_ventana = 500
    alto_ventana = 250
    
    v_creacion = tk.Toplevel()
    v_creacion.title("Creación de Máquina Virtual")

    x_ventana = v_creacion.winfo_screenwidth() // 2 - ancho_ventana // 2
    y_ventana = v_creacion.winfo_screenheight() // 2 - alto_ventana // 2

    posicion = str(ancho_ventana) + "x" + str(alto_ventana) + "+" + str(x_ventana) + "+" + str(y_ventana)
    v_creacion.geometry(posicion)
    
    herramientas = tk.Frame(v_creacion, bd=1, relief=tk.RAISED)

    cancelar = tk.Button(herramientas, text="Cancelar", command=v_creacion.destroy)
    cancelar.pack(side=tk.RIGHT, padx=7, pady=2)

    crearVM = tk.Button(herramientas, text="Crear VM", command=crear_vm)
    crearVM.pack(side=tk.RIGHT, padx=7, pady=2)

    

    def seleccionar_iso():
        filename = filedialog.askopenfilename(filetypes=[("ISO files", "*.iso")])
        if filename:
            iso_btn.config(state="disabled")
            iso_entry.delete(0, tk.END)
            iso_entry.insert(0, filename)

    herramientas.pack(side=tk.BOTTOM, fill=tk.X)

    lbl_creacion = tk.Label(v_creacion, text="Nombre de la VM:")
    lbl_creacion.place(x=30, y=20)
    nombre_entry = tk.Entry(v_creacion, width=37)
    nombre_entry.place(x=160, y=20)

    lbl_memoria = tk.Label(v_creacion, text="Memoria (MB):")
    lbl_memoria.place(x=30, y=50)
    memoria_entry = tk.Entry(v_creacion, width=37)
    memoria_entry.place(x=160, y=50)

    lbl_cpu = tk.Label(v_creacion, text="Número de CPUs:")
    lbl_cpu.place(x=30, y=80)
    cpu_entry = tk.Entry(v_creacion, width=37)
    cpu_entry.place(x=160, y=80)

    lbl_almacenamiento = tk.Label(v_creacion, text="Disco (GB):")
    lbl_almacenamiento.place(x=30, y=110)

    almacenamiento_entry = tk.Entry(v_creacion, width=37)
    almacenamiento_entry.place(x=160, y=110)

    lbl_iso = tk.Label(v_creacion, text="Imagen ISO:")
    lbl_iso.place(x=30, y=140)
    iso_btn = tk.Button(v_creacion, text="Seleccionar archivo", command=seleccionar_iso)
    iso_btn.place(x=160, y=140)

    iso_entry = tk.Entry(v_creacion, width=37)
    iso_entry.place(x=160, y=170)
