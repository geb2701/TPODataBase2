/* global use, db */
// MongoDB Playground
// Use Ctrl+Space inside a snippet or a string literal to trigger completions.

const database = 'talentum';
const collection = 'ofertas';

// The current database to use.
use(database);

db.ofertas.insertMany([
  {
    puesto: "Backend Developer",
    empresa: "Globant",
    categoria: "Desarrollo",
    fecha_publicacion: ISODate("2024-05-01"),
    requisitos: ["Java", "Spring Boot", "MongoDB"],
    beneficios: ["Home office", "Bono anual", "Prepaga"],
    estado: "Activa",
    ubicacion: "Remoto"
  },
  {
    puesto: "Full Stack Developer",
    empresa: "Mercado Libre",
    categoria: "Desarrollo",
    fecha_publicacion: ISODate("2024-04-25"),
    requisitos: ["Node.js", "React", "PostgreSQL"],
    beneficios: ["Stock options", "Capacitación", "Obra social"],
    estado: "Activa",
    ubicacion: "Buenos Aires"
  },
  {
    puesto: "Data Analyst",
    empresa: "Accenture",
    categoria: "Data",
    fecha_publicacion: ISODate("2024-03-15"),
    requisitos: ["SQL", "Python", "Tableau"],
    beneficios: ["Obra social", "Horario flexible"],
    estado: "Cerrada",
    ubicacion: "Híbrido"
  }
]);

