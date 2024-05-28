import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
import libvirt
import crearVM as C
import iniciarVM as I
import subprocess
import os

#ventana principal
ventana = tk.Tk()
ventana.title("Gestor de Maquinas Virtuales")
# ventana.state('zoomed')
# ventana.state("normal")
ventana.geometry("1200x800")
# ventana.iconbitmap('virtual.ico')

vm_seleccionada = None

def seleccionar_vm(event, vm_nombre):
    global vm_seleccionada
    vm_seleccionada = vm_nombre


    for widget in info_vm.winfo_children():
        widget.config(relief=tk.RAISED, bd=2)

    event.widget.config(relief=tk.SOLID, bd=4, highlightbackground="blue")

    conn = libvirt.open('qemu:///system')
    if conn is None:
        print('No se pudo conectar al hipervisor')
        return

    try:
        vm = conn.lookupByName(vm_nombre)
        if vm is None:
            print(f'No se pudo encontrar la VM con nombre {vm_nombre}')
            return
        
        nombre_entry.config(state="normal")
        nombre_entry.delete(0, tk.END)
        nombre_entry.insert(0, vm_nombre)
        nombre_entry.config(state="readonly")

        memoria_entry.config(state="normal")
        memoria_entry.delete(0, tk.END)
        memoria_entry.insert(0, str(vm.maxMemory() // 1024))
        memoria_entry.config(state="readonly")

        cpu_entry.config(state="normal")
        cpu_entry.delete(0, tk.END)
        cpu_entry.insert(0, str(vm.maxVcpus()))
        cpu_entry.config(state="readonly")


        vm_xml = vm.XMLDesc()
        root = ET.fromstring(vm_xml)
        almacenamiento = root.find(".//disk[@device='disk']/source").get('file')
        almacenamiento_entry.config(state="normal")
        almacenamiento_entry.delete(0, tk.END)
        almacenamiento_entry.insert(0, almacenamiento)
        almacenamiento_entry.config(state="readonly")

    except Exception as e:
        print(f'Error al obtener la información de la máquina virtual: {e}')
    finally:
        conn.close()



def abrir_crear():
    C.crear(ventana, info_vm, seleccionar_vm)



def iniciar_vm(nombre_vm):
    conn = libvirt.open('qemu:///system')
    if conn is None:
        print('No se pudo conectar al hipervisor')
        return
    
    vm = conn.lookupByName(nombre_vm)

    if vm.isActive() == 0:
        subprocess.run(['virsh', 'start', nombre_vm])

    os.system(f'virt-viewer --attach {nombre_vm}')


def iniciar_maquina():
    if vm_seleccionada:
        iniciar_vm(vm_seleccionada)
    else:
        print('No se ha seleccionado ninguna VM')





def detener_vm(nombre_vm):
    conn = libvirt.open('qemu:///system')
    if conn is None:
        print('No se pudo conectar al hipervisor')
        return
    
    vm = conn.lookupByName(nombre_vm)

    if vm.isActive() == 1:
        vm.shutdown()
        print(f'VM {nombre_vm} detenida')
    else:
        print(f'VM {nombre_vm} ya está detenida')

def detener_maquina():
    if vm_seleccionada:
        detener_vm(vm_seleccionada)
    else:
        print('No se ha seleccionado ninguna VM')





barra_menus = tk.Menu()
ventana.config(menu=barra_menus)

menu_archivo = tk.Menu(barra_menus, tearoff=0)

menu_archivo.add_command(
    label="Salir",
    command=ventana.quit
)

barra_menus.add_cascade(menu=menu_archivo, label="Archivo")



herramientas = tk.Frame(ventana, bd=1, relief=tk.RAISED)

crear = tk.Button(herramientas, text="Crear VM", width=15, height=2, command=abrir_crear)
crear.pack(side=tk.LEFT, padx=7, pady=10)

iniciar = tk.Button(herramientas, text="Iniciar VM", width=15, height=2, command=iniciar_maquina)
iniciar.pack(side=tk.LEFT, padx=7, pady=10)

detener = tk.Button(herramientas, text="Detener VM", width=15, height=2, command=detener_maquina)
detener.pack(side=tk.LEFT, padx=7, pady=10)

reiniciar = tk.Button(herramientas, text="Reiniciar VM", width=15, height=2)
reiniciar.pack(side=tk.LEFT, padx=7, pady=10)

eliminar = tk.Button(herramientas, text="Eliminar VM", width=15, height=2)
eliminar.pack(side=tk.LEFT, padx=7, pady=10)

herramientas.pack(side=tk.TOP, fill=tk.X)



panedwindow = ttk.Panedwindow(ventana, orient=tk.HORIZONTAL)
panedwindow.pack(fill=tk.BOTH, expand=True)

info_vm = tk.Frame(panedwindow, bd=1, relief=tk.SUNKEN, bg="dark grey", width=60)
panedwindow.add(info_vm, weight=1)

main_area = tk.Frame(panedwindow, bg="white", relief=tk.SUNKEN)
panedwindow.add(main_area, weight=3)


lbl_creacion = tk.Label(main_area, text="Nombre de la VM:")
lbl_creacion.place(x=100, y=20)
nombre_entry = tk.Entry(main_area, width=37, state="readonly")
nombre_entry.place(x=230, y=20)

lbl_memoria = tk.Label(main_area, text="Memoria (MB):")
lbl_memoria.place(x=100, y=50)
memoria_entry = tk.Entry(main_area, width=37, state="readonly")
memoria_entry.place(x=230, y=50)

lbl_cpu = tk.Label(main_area, text="Número de CPUs:")
lbl_cpu.place(x=100, y=80)
cpu_entry = tk.Entry(main_area, width=37, state="readonly")
cpu_entry.place(x=230, y=80)

lbl_almacenamiento = tk.Label(main_area, text="Disco (GB):")
lbl_almacenamiento.place(x=100, y=110)
almacenamiento_entry = tk.Entry(main_area, width=37, state="readonly")
almacenamiento_entry.place(x=230, y=110)


C.actualizar_lista_vms(info_vm, seleccionar_vm)

ventana.mainloop()