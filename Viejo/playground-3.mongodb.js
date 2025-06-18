// MongoDB Playground
// Use Ctrl+Space inside a snippet or a string literal to trigger completions.

// The current database to use.
use('talentum');

// Create a new document in the collection.
db.candidatos.insertMany([
  {
    nombre: "Josefina López",
    email: "Josefina.lopez@mail.com",
    skills_tecnicos: ["Java", "MongoDB", "Spring Boot"],
    skills_blandos: ["Trabajo en equipo", "Liderazgo"],
    experiencia: [
      { empresa: "Globant", rol: "Backend Dev", años: 2 }
    ],
    historial_procesos: [],
    evaluaciones: []
  },
  {
    nombre: "Luis Gómez",
    email: "luisg@mail.com",
    skills_tecnicos: ["Python", "Django", "PostgreSQL"],
    skills_blandos: ["Resolución de problemas"],
    experiencia: [
      { empresa: "Mercado Libre", rol: "Full Stack", años: 3 }
    ],
    historial_procesos: [],
    evaluaciones: []
  },
  {
    nombre: "Clara Méndez",
    email: "clara.mendez@mail.com",
    skills_tecnicos: ["Node.js", "React", "MongoDB"],
    skills_blandos: ["Comunicación", "Creatividad"],
    experiencia: [
      { empresa: "Despegar", rol: "Frontend Dev", años: 1 }
    ],
    historial_procesos: [],
    evaluaciones: []
  }
]);

