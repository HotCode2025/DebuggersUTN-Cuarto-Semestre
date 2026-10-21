package utn.tienda_libros.vista;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import utn.tienda_libros.modelo.Libro;
import utn.tienda_libros.servicio.LibroServicio;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.Locale;
//import
import javax.swing.SwingConstants;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.TableColumn;
import javax.swing.table.TableColumnModel;

@Component
public class LibroFrom extends JFrame {
    LibroServicio libroServicio;
    private JPanel panel;
    private JTable tablaLibros;
    private JTextField idTexto;
    private JLabel Libro;
    private JTextField libroTexto;
    private JTextField autorTexto;
    private JTextField precioTexto;
    private JTextField existenciaTexto;
    private JButton agregarButton;
    private JButton modificarButton;
    private JButton eliminarButton;
    private DefaultTableModel tablaModeloLibros;

    @Autowired
    public LibroFrom(LibroServicio libroServicio) {
        this.libroServicio = libroServicio;
        iniciarForma();
        agregarButton.addActionListener(e -> agregarLibro() );

        tablaLibros.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                super.mouseClicked(e);
                cargarLibroSeleccionado();
            }
        });

        modificarButton.addActionListener(e -> modificarLibro());

        eliminarButton.addActionListener(e -> eliminarLibro());
    }

    private void iniciarForma() {
        setContentPane(panel);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setVisible(true);
        setSize(950, 700);

        // Para obtener las dimensiones de la ventana
        Toolkit toolkit = Toolkit.getDefaultToolkit();
        Dimension tamanioPantalla = toolkit.getScreenSize();
        int x = (tamanioPantalla.width - getWidth() / 2);
        int y = (tamanioPantalla.height - getHeight() / 2);
        setLocation(x, y);
    }

    private void agregarLibro() {
        // Si hay un id cargado, deberia usar el boton modificar y no el agregar
        if (!idTexto.getText().isEmpty()) {
            mostrarMensaje("Hay un libro seleccionado. Usa el botón Modificar para editarlo.");
            return;
        }
        // Leer los valores del formulario
        if (libroTexto.getText().equals("")) {
            mostrarMensaje("Ingresa el nombre del libro");
            libroTexto.requestFocusInWindow();
            return;
        }
        var nombreLibro = libroTexto.getText();
        var autor = autorTexto.getText();
        var precio = Double.parseDouble(precioTexto.getText());
        var existencia = Integer.parseInt(existenciaTexto.getText());

        // Creamos el objeto libro
        var libro = new Libro(null, nombreLibro, autor, precio, existencia);
        // libro.setNombreLibro(nombreLibro);
        // libro.setAutor(autor);
        // libro.setPrecio(precio);
        // libro.setExistencias(existencia);

        this.libroServicio.guardarLibro(libro);
        mostrarMensaje("Se agrego el libro");
        limpiarFormulario();

        // Recargamos la tabla de libros
        listarLibros();
    }

    private void cargarLibroSeleccionado() {
        // Los indices de las columnas inician en 0
        var renglon = tablaLibros.getSelectedRow();
        if (renglon != -1) {
            String idLibros = tablaLibros.getModel().getValueAt(renglon, 0).toString();
            idTexto.setText(idLibros);

            String nombreLibro = tablaLibros.getModel().getValueAt(renglon, 1).toString();
            libroTexto.setText(nombreLibro);

            String autor = tablaLibros.getModel().getValueAt(renglon, 2).toString();
            autorTexto.setText(autor);

            String precio = tablaLibros.getModel().getValueAt(renglon, 3).toString();
            precioTexto.setText(precio);

            String existencia = tablaLibros.getModel().getValueAt(renglon, 4).toString();
            existenciaTexto.setText(existencia);
        }
    }

    private void modificarLibro() {
        if (this.idTexto.equals("")) {
            mostrarMensaje("Debes seleccionar un registro en la tabla");
        }
        else {
            // Verificamos que el nombre del libro no este vacio
            if (libroTexto.getText().equals("")) {
                mostrarMensaje("Ingrese el nombre del libro");
                libroTexto.requestFocusInWindow();
                return;
            }
            // Llenamos el objeto libro con los datos actualizados
            int idLibro = Integer.parseInt(idTexto.getText());
            var nombreLibro = libroTexto.getText();
            var autor = autorTexto.getText();
            var precio = Double.parseDouble(precioTexto.getText());
            var existencia = Integer.parseInt(existenciaTexto.getText());
            var libro = new Libro(idLibro, nombreLibro, autor, precio, existencia);
            libroServicio.guardarLibro(libro);
            mostrarMensaje("Se modifico el libro");
            limpiarFormulario();
            listarLibros();
        }
    }

    private void eliminarLibro() {
        var renglon = tablaLibros.getSelectedRow();
        if (renglon != -1) {
            String idLibro = tablaLibros.getModel().getValueAt(renglon, 0).toString();
            idTexto.setText(idLibro);
            var libro = new Libro();
            libro.setIdLibro(Integer.parseInt(idLibro));
            libroServicio.eliminarLibro(libro);
            mostrarMensaje("Libro " + idLibro + " ELIMINADO");
            limpiarFormulario();
            listarLibros();
        }
        else {
            mostrarMensaje("No se ha seleccionado un libro de la tabla a eliminar");
        }
    }

    private void limpiarFormulario() {
        idTexto.setText("");
        libroTexto.setText("");
        autorTexto.setText("");
        precioTexto.setText("");
        existenciaTexto.setText("");
        tablaLibros.clearSelection();
    }

    private void mostrarMensaje(String mensaje) {
        JOptionPane.showMessageDialog(this, mensaje);
    }

    private void createUIComponents() {
        idTexto = new JTextField("");
        idTexto.setVisible(false);
        this.tablaModeloLibros = new DefaultTableModel(0 , 5) {
            @Override
            public boolean isCellEditable(int row, int column) {
                return false;
            }
        };
        String[] cabecera = {"Id", "Libro", "Autor", "Precio", "Existencia"};
        this.tablaModeloLibros.setColumnIdentifiers(cabecera);

        // Instanciar el objeto de JTable
        this.tablaLibros = new JTable(tablaModeloLibros);

        // Evitamos que se seleccionen varios registros
        tablaLibros.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);

        // Ajustamos al ancho de las columnas y la ubicacion del texto
        ajustarColumnas();
        listarLibros();
    }

    private void listarLibros() {
        // Limpiar la tabla
        tablaModeloLibros.setRowCount(0);

        // Obtener los libros de la BD
        var libros = libroServicio.listarLibros();

        // Iteramos cada libro
        libros.forEach((libro) -> { // funcion Lambda
            // Creamos cadas registro para agregarlo a la tabla
            Object[] renglonLibro = {
                libro.getIdLibro(),
                libro.getNombreLibro(),
                libro.getAutor(),
                libro.getPrecio(),
                libro.getExistencias(),
            };
            this.tablaModeloLibros.addRow(renglonLibro);
        });
    }

    private void ajustarColumnas() {
        TableColumnModel columnas = tablaLibros.getColumnModel();
        // Guardo el ancho de una columna normal
        int anchoNormal = columnas.getColumn(1).getPreferredWidth();

        TableColumn colId = columnas.getColumn(0);
        colId.setPreferredWidth(anchoNormal / 4);
        TableColumn colPrecio = columnas.getColumn(3);
        colPrecio.setPreferredWidth(anchoNormal / 2);
        TableColumn colExistencia = columnas.getColumn(4);
        colExistencia.setPreferredWidth(anchoNormal / 3);

        // Texto centrado en ID, Existencia
        DefaultTableCellRenderer centrado = new DefaultTableCellRenderer();
        centrado.setHorizontalAlignment(SwingConstants.CENTER);
        colId.setCellRenderer(centrado);
        columnas.getColumn(4).setCellRenderer(centrado);

        // Precio: centrado y con 2 decimales
        DefaultTableCellRenderer precio = new DefaultTableCellRenderer() {
            @Override
            protected void setValue(Object value) {
                if (value instanceof Number) {
                    setText(String.format(Locale.US, "%.2f", ((Number) value).doubleValue()));
                } else {
                    super.setValue(value);
                }
            }
        };
        precio.setHorizontalAlignment(SwingConstants.CENTER);
        columnas.getColumn(3).setCellRenderer(precio);
    }
}
