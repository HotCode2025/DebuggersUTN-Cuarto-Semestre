package UTN.estudiantes.servicio;

import UTN.estudiantes.modelo.Estudiantes2026;
import UTN.estudiantes.repositorio.EstudianteRepositorio;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class EstudianteServicio implements IEstudianteServicio{
    @Autowired

    private EstudianteRepositorio estudianteRepositorio;

    @Override
    public List<Estudiantes2026> listarEstudiantes() {
        List<Estudiantes2026> estudiantes = estudianteRepositorio.findAll();
        return estudiantes;
    }

    @Override
    public Estudiantes2026 buscarEstudiantePorId(Integer idEstudiantes2026) {
        Estudiantes2026 estudiante = estudianteRepositorio.findById(idEstudiantes2026).orElse(null); //tambien existe orElseThrow
        return estudiante;
    }

    @Override
    public void guardarEstudiante(Estudiantes2026 estudiante) {
        estudianteRepositorio.save(estudiante);
    }

    @Override
    public void eliminarEstudiante(Estudiantes2026 estudiante) {
        estudianteRepositorio.delete(estudiante);
    }
}
