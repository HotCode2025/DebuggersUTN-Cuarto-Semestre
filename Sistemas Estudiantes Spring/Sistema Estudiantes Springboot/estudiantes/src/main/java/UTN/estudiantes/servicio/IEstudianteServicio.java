package UTN.estudiantes.servicio;

import UTN.estudiantes.modelo.Estudiantes2026;

import java.util.List;

public interface IEstudianteServicio {
    public List<Estudiantes2026> listarEstudiantes();
    public Estudiantes2026 buscarEstudiantePorId (Integer idEstudiante);
    public void guardarEstudiante(Estudiantes2026 estudiante);
    public void eliminarEstudiante(Estudiantes2026 estudiante);
}
