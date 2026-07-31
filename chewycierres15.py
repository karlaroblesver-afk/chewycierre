import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración inicial de la página
st.set_page_config(
    page_title="Chewy - Control de Turnos", 
    page_icon="🍪", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# Estilos CSS avanzados: incluye ocultar elementos innecesarios al momento de imprimir
st.markdown("""
    <style>
    .main {
        background-color: #fcf9f2;
    }
    .bienvenida-box {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 20px;
        border-radius: 12px;
        color: #4a2e18;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .ticket-box {
        background-color: #ffffff;
        border: 2px dashed #d35400;
        padding: 20px;
        border-radius: 10px;
        font-family: 'Courier New', Courier, monospace;
        color: #333333;
        margin-top: 15px;
    }
    .stButton>button {
        background-color: #d35400;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        width: 100%;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #e67e22;
        color: white;
    }

    /* ESTILOS PARA IMPRESIÓN REAL EN PAPEL O PDF */
    @media print {
        body * {
            visibility: hidden;
        }
        #printable-ticket, #printable-ticket * {
            visibility: visible;
        }
        #printable-ticket {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            border: none;
        }
        .no-print {
            display: none !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar almacenamiento persistente de cuentas y turnos
if "usuarios_registrados" not in st.session_state:
    st.session_state.usuarios_registrados = {
        "admin@chewy.com": {"nombre": "Administrador Chewy", "pass": "1234", "rol": "Administrador"}
    }

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario_actual = ""
    st.session_state.rol_actual = ""

if "historial_cierres" not in st.session_state:
    st.session_state.historial_cierres = []

if "ultimo_ticket" not in st.session_state:
    st.session_state.ultimo_ticket = None

# ==================== PANTALLA DE LOGIN Y REGISTRO ====================
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center; color: #d35400;'>🍪 Chewy - Control de Turnos</h1>", unsafe_allow_html=True)
    
    opcion = st.radio("Selecciona una opción:", ["Iniciar Sesión", "Crear Nueva Cuenta con Correo"], horizontal=True)

    if opcion == "Iniciar Sesión":
        st.subheader("🔐 Iniciar Sesión en Chewy")
        with st.form("form_login"):
            correo_ingresado = st.text_input("Correo electrónico:")
            pass_ingresada = st.text_input("Contraseña:", type="password")
            btn_entrar = st.form_submit_button("Entrar a Chewy")
            
            if btn_entrar:
                if correo_ingresado in st.session_state.usuarios_registrados and st.session_state.usuarios_registrados[correo_ingresado]["pass"] == pass_ingresada:
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = st.session_state.usuarios_registrados[correo_ingresado]["nombre"]
                    st.session_state.rol_actual = st.session_state.usuarios_registrados[correo_ingresado]["rol"]
                    st.rerun()
                else:
                    st.error("❌ Correo o contraseña incorrectos. (Prueba con admin@chewy.com / 1234)")
    else:
        st.subheader("📝 Registrar Nueva Cuenta en Chewy")
        with st.form("form_registro"):
            reg_nombre = st.text_input("Nombre de la persona:")
            reg_correo = st.text_input("Correo electrónico (Ej. cajero@chewy.com):")
            reg_pass = st.text_input("Contraseña:", type="password")
            reg_rol = st.selectbox("Rol", ["Cajero", "Administrador"])
            btn_registro = st.form_submit_button("Crear Cuenta")
            
            if btn_registro:
                if not reg_correo or not reg_pass or not reg_nombre:
                    st.warning("⚠️ Llena todos los campos.")
                elif reg_correo in st.session_state.usuarios_registrados:
                    st.error("❌ Este correo ya está registrado.")
                else:
                    # Guardar permanentemente en la sesión actual
                    st.session_state.usuarios_registrados[reg_correo] = {
                        "nombre": reg_nombre,
                        "pass": reg_pass,
                        "rol": reg_rol
                    }
                    st.success("¡Cuenta creada con éxito! Ahora selecciona 'Iniciar Sesión' arriba para entrar.")

# ==================== APLICACIÓN PRINCIPAL (CHEWY) ====================
else:
    st.sidebar.title(f"👤 Menú Chewy")
    st.sidebar.write(f"Usuario: **{st.session_state.usuario_actual}**")
    st.sidebar.write(f"Rol: **{st.session_state.rol_actual}**")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario_actual = ""
        st.session_state.rol_actual = ""
        st.rerun()

    # MENSAJE DE BIENVENIDA APARTADO Y CON COLOR
    st.markdown(f"""
        <div class="bienvenida-box">
            <h2>¡Hola, {st.session_state.usuario_actual}! 👋</h2>
            <p>Bienvenido/a al panel de control de <b>Chewy</b>. Todo listo para registrar un turno exitoso.</p>
        </div>
    """, unsafe_allow_html=True)

    st.title("🍪 Chewy - Registro de Cierres de Turno")
    st.write("Control financiero completo de ventas, gastos, abonos y tickets.")

    with st.container():
        st.subheader("📝 Datos Generales del Turno")
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            responsable = st.text_input("A cargo:", value=st.session_state.usuario_actual)
        with col_r2:
            turno = st.selectbox("Turno", ["Matutino", "Vespertino", "Turno Completo"])
        with col_r3:
            fecha = st.date_input("Fecha", datetime.now())

        st.markdown("---")
        st.subheader("💵 Efectivo, Caja y Formas de Pago")
        col1, col2 = st.columns(2)
        with col1:
            caja_entrada = st.number_input("Efectivo Inicial en Caja (Fondo $):", min_value=0.0, format="%.2f", value=0.0)
            efectivo_vendido = st.number_input("Venta Real en Efectivo ($):", min_value=0.0, format="%.2f", value=0.0)
            tarjeta = st.number_input("Ventas con Tarjeta ($):", min_value=0.0, format="%.2f", value=0.0)
        with col2:
            caja_salida = st.number_input("Efectivo Físico Total en Caja al Final ($):", min_value=0.0, format="%.2f", value=0.0)
            transferencia = st.number_input("Ventas por Transferencia ($):", min_value=0.0, format="%.2f", value=0.0)

        st.markdown("---")
        st.subheader("💸 Desglose de Gastos del Turno (Amplio)")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            g1_concepto = st.text_input("Gasto 1 - Concepto", value="")
            g2_concepto = st.text_input("Gasto 2 - Concepto", value="")
            g3_concepto = st.text_input("Gasto 3 - Concepto", value="")
        with col_g2:
            g1_monto = st.number_input("Gasto 1 - Monto ($)", min_value=0.0, format="%.2f", value=0.0)
            g2_monto = st.number_input("Gasto 2 - Monto ($)", min_value=0.0, format="%.2f", value=0.0)
            g3_monto = st.number_input("Gasto 3 - Monto ($)", min_value=0.0, format="%.2f", value=0.0)

        lista_gastos_datos = []
        total_gastos = 0.0

        for con, mon in [(g1_concepto, g1_monto), (g2_concepto, g2_monto), (g3_concepto, g3_monto)]:
            if mon > 0 and con.strip():
                lista_gastos_datos.append(f"{con.strip()}: ${mon:.2f}")
                total_gastos += mon

        texto_gastos_resumen = " | ".join(lista_gastos_datos) if lista_gastos_datos else "Sin gastos"
        st.info(f"💡 **Total de Gastos Reales Calculados:** ${total_gastos:.2f}")

        st.markdown("---")
        st.subheader("💼 Sueldos Pagados")
        sueldos = st.number_input("Sueldos pagados en el turno ($):", min_value=0.0, format="%.2f", value=0.0)

        st.markdown("---")
        st.subheader("👥 Créditos y Abonos de Clientes (Amplio)")
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            c1_nombre = st.text_input("Cliente 1", value="")
            c2_nombre = st.text_input("Cliente 2", value="")
        with col_c2:
            c1_monto = st.number_input("Abono C1 ($)", min_value=0.0, format="%.2f", value=0.0)
            c2_monto = st.number_input("Abono C2 ($)", min_value=0.0, format="%.2f", value=0.0)
        with col_c3:
            c1_metodo = st.selectbox("Método C1", ["Efectivo", "Tarjeta"])
            c2_metodo = st.selectbox("Método C2", ["Efectivo", "Tarjeta"])

        lista_creditos_datos = []
        creditos_efectivo_extra = 0.0
        creditos_tarjeta_extra = 0.0

        for nom, mon, met in [(c1_nombre, c1_monto, c1_metodo), (c2_nombre, c2_monto, c2_metodo)]:
            if mon > 0 and nom.strip():
                lista_creditos_datos.append(f"{nom.strip()}: ${mon:.2f} ({met})")
                if met == "Efectivo":
                    creditos_efectivo_extra += mon
                else:
                    creditos_tarjeta_extra += mon

        texto_creditos_resumen = " | ".join(lista_creditos_datos) if lista_creditos_datos else "Ninguno"

        ganancia_manual = st.number_input("Ganancia Manual [Opcional - dejar en 0 para cálculo automático]:", min_value=0.0, format="%.2f", value=0.0)
        observaciones = st.text_area("Observaciones del turno")

        if st.button("💾 Guardar Cierre de Turno en Chewy", type="primary"):
            ventas_efectivo_totales = efectivo_vendido + creditos_efectivo_extra
            ventas_tarjeta_totales = tarjeta + creditos_tarjeta_extra

            efectivo_esperado = caja_entrada + ventas_efectivo_totales - (total_gastos + sueldos)
            diferencia_caja = caja_salida - efectivo_esperado

            if ganancia_manual > 0:
                ganancia_turno = ganancia_manual
            else:
                ganancia_turno = (ventas_efectivo_totales + ventas_tarjeta_totales + transferencia) - (total_gastos + sueldos)

            nuevo_cierre = {
                "Fecha": pd.to_datetime(fecha).date(),
                "Responsable": responsable,
                "Turno": turno,
                "Venta_Efectivo": ventas_efectivo_totales,
                "Venta_Tarjeta": ventas_tarjeta_totales,
                "Caja_Final": caja_salida,
                "Diferencia_Caja": diferencia_caja,
                "Total_Gastos": total_gastos,
                "Detalle_Gastos": texto_gastos_resumen,
                "Sueldos": sueldos,
                "Detalle_Creditos": texto_creditos_resumen,
                "Ganancia_Turno": ganancia_turno,
                "Observaciones": observaciones
            }
            
            st.session_state.historial_cierres.append(nuevo_cierre)
            st.session_state.ultimo_ticket = nuevo_cierre
            st.success("¡Turno guardado y sumado correctamente en Chewy!")

    # ==================== VISTA PREVIA E IMPRESIÓN DEL TICKET ====================
    if st.session_state.ultimo_ticket is not None:
        st.markdown("---")
        st.subheader("🧾 Ticket de Resumen para Impresora Térmica")
        st.write("Haz clic en el botón para activar la impresión directa del navegador:")

        t = st.session_state.ultimo_ticket
        
        # Renderizado limpio del ticket con ID único para impresión instantánea
        st.markdown(f"""
        <div id="printable-ticket" class="ticket-box">
            <center>
                <b>🍪 GALLETAS CHEWY 🍪</b><br>
                CORTE DE TURNO<br>
                --------------------------------<br>
            </center>
            <b>Fecha:</b> {t['Fecha']}<br>
            <b>Responsable:</b> {t['Responsable']}<br>
            <b>Turno:</b> {t['Turno']}<br>
            --------------------------------<br>
            <b>INGRESOS (Con Abonos):</b><br>
            - Efectivo Total: ${t['Venta_Efectivo']:.2f}<br>
            - Tarjeta Total: ${t['Venta_Tarjeta']:.2f}<br>
            --------------------------------<br>
            <b>GASTOS Y PAGOS:</b><br>
            - Gastos: ${t['Total_Gastos']:.2f}<br>
            - Sueldos: ${t['Sueldos']:.2f}<br>
            --------------------------------<br>
            <b>CAJA:</b><br>
            - Efectivo Final: ${t['Caja_Final']:.2f}<br>
            - Diferencia: ${t['Diferencia_Caja']:.2f}<br>
            --------------------------------<br>
            <b>GANANCIA TURNO: ${t['Ganancia_Turno']:.2f}</b><br>
            <center>
                --------------------------------<br>
                ¡GRACIAS POR SU ESFUERZO!<br>
                Chewy System v2.0
            </center>
        </div>
        """, unsafe_allow_html=True)

        # Script de JavaScript integrado que llama limpiamente al comando window.print() del navegador nativo
        st.markdown("""
        <script>
        function triggerPrint() {
            window.print();
        }
        </script>
        <button onclick="triggerPrint()" class="no-print" style="background-color: #d35400; color: white; border-radius: 8px; font-weight: bold; border: none; width: 100%; padding: 12px; cursor: pointer; margin-top: 10px;">
            🖨️ Imprimir Ticket de Corte Ahora
        </button>
        """, unsafe_allow_html=True)

    # ==================== PANEL DE ADMINISTRADOR ====================
    if st.session_state.rol_actual == "Administrador":
        if st.session_state.historial_cierres:
            st.markdown("---")
            st.subheader("📊 [ADMIN CHEWY] Panel de Resumen Financiero y Gráficas")

            df = pd.DataFrame(st.session_state.historial_cierres)
            
            hoy = datetime.now().date()
            ganancia_dia_actual = df[df["Fecha"] == hoy]["Ganancia_Turno"].sum()
            semana_actual = datetime.now().isocalendar()[1]
            ganancia_semana = df[pd.to_datetime(df["Fecha"]).dt.isocalendar().week == semana_actual]["Ganancia_Turno"].sum()
            mes_actual = datetime.now().month
            anio_actual = datetime.now().year
            ganancia_mes = df[(pd.to_datetime(df["Fecha"]).dt.month == mes_actual) & (pd.to_datetime(df["Fecha"]).dt.year == anio_actual)]["Ganancia_Turno"].sum()

            col_d, col_s, col_m = st.columns(3)
            col_d.metric("Ganancia Hoy", f"${ganancia_dia_actual:.2f}")
            col_s.metric("Ganancia Semana", f"${ganancia_semana:.2f}")
            col_m.metric("Ganancia Mes", f"${ganancia_mes:.2f}")

            st.markdown("---")
            st.subheader("📈 Visualización Gráfica Interactiva")
            
            tipo_grafica = st.selectbox(
                "Selecciona el tipo de gráfica a visualizar:",
                ["Ganancias por Turno y Fecha (Barras)", "Comparativa: Efectivo vs Tarjeta"]
            )

            if tipo_grafica == "Ganancias por Turno y Fecha (Barras)":
                if not df.empty:
                    df_grafica = df.copy()
                    df_grafica["Etiqueta"] = df_grafica["Fecha"].astype(str) + " (" + df_grafica["Turno"] + ")"
                    st.bar_chart(df_grafica.set_index("Etiqueta")[["Ganancia_Turno"]])
            else:
                if not df.empty:
                    st.bar_chart(df.set_index("Responsable")[["Venta_Efectivo", "Venta_Tarjeta"]])

            st.markdown("---")
            st.subheader("📋 [ADMIN CHEWY] Historial Consolidado por Día")
            df_diario = df.groupby("Fecha").agg({
                "Venta_Efectivo": "sum",
                "Venta_Tarjeta": "sum",
                "Caja_Final": "last",
                "Total_Gastos": "sum",
                "Sueldos": "sum",
                "Ganancia_Turno": "sum"
            }).reset_index()
            st.dataframe(df_diario)

            st.markdown("---")
            st.subheader("📑 [ADMIN CHEWY] Detalle Completo de Turnos")
            df_dataframe_detalle = df[["Fecha", "Responsable", "Turno", "Venta_Efectivo", "Venta_Tarjeta", "Caja_Final", "Detalle_Creditos", "Detalle_Gastos", "Ganancia_Turno", "Observaciones"]]
            st.dataframe(df_dataframe_detalle)
    else:
        st.markdown("---")
        st.info("🔒 Turno registrado con éxito en **Chewy**. Las métricas financieras y gráficas avanzadas están protegidas para el perfil de **Administrador**.")
