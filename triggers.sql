--logs de Pessoa
CREATE OR REPLACE FUNCTION pessoalog() RETURNS TRIGGER AS $$
DECLARE
    tipo char(1);
BEGIN
    IF TG_OP = 'UPDATE' THEN
        tipo:='U';
		INSERT INTO pessoalog VALUES (LOCALTIMESTAMP,tipo,OLD.rga,OLD.cpf,NEW.rga,NEW.cpf);
    	RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        tipo:='D';
		INSERT INTO pessoalog VALUES (LOCALTIMESTAMP,tipo,OLD.rga,OLD.cpf,NEW.rga,NEW.cpf);
    	RETURN OLD;
    END IF;
END;
$$ LANGUAGE PLPGSQL;

CREATE TRIGGER pessoalog BEFORE DELETE OR UPDATE OF rga,cpf ON pessoa FOR EACH ROW EXECUTE PROCEDURE pessoalog();

--logs de professor
CREATE OR REPLACE FUNCTION professorlog() RETURNS TRIGGER AS $$
DECLARE
    tipo char(1);
BEGIN
    IF TG_OP = 'UPDATE' THEN
        tipo:='U';
		INSERT INTO professorlog VALUES (LOCALTIMESTAMP,tipo,OLD.rga_prof,NEW.rga_prof);
		RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        tipo:='D';
		INSERT INTO professorlog VALUES (LOCALTIMESTAMP,tipo,OLD.rga_prof,NEW.rga_prof);
    	RETURN OLD;
    END IF;
END;
$$ LANGUAGE PLPGSQL;

CREATE TRIGGER professorlog BEFORE DELETE OR UPDATE OF rga_prof ON professor FOR EACH ROW EXECUTE PROCEDURE professorlog();

--logs de aluno
CREATE OR REPLACE FUNCTION alunolog() RETURNS TRIGGER AS $$
DECLARE
    tipo char(1);
BEGIN
    IF TG_OP = 'UPDATE' THEN
        tipo:='U';
		INSERT INTO alunolog VALUES (LOCALTIMESTAMP,tipo,OLD.rga_aluno,OLD.cod_curso,NEW.rga_aluno,NEW.cod_curso);
		RETURN NEW;  
    ELSIF TG_OP = 'DELETE' THEN
        tipo:='D';
		INSERT INTO alunolog VALUES (LOCALTIMESTAMP,tipo,OLD.rga_aluno,OLD.cod_curso,NEW.rga_aluno,NEW.cod_curso);
		RETURN OLD;  
    END IF;         
END;
$$ LANGUAGE PLPGSQL;

CREATE TRIGGER alunolog BEFORE DELETE OR UPDATE OF rga_aluno, cod_curso ON aluno FOR EACH ROW EXECUTE PROCEDURE alunolog();

--logs de disciplina
CREATE OR REPLACE FUNCTION disciplinalog() RETURNS TRIGGER AS $$
DECLARE
    tipo char(1);
BEGIN
    IF TG_OP = 'UPDATE' THEN
        tipo:='U';
		INSERT INTO disciplinalog VALUES (LOCALTIMESTAMP,tipo,OLD.cod_disciplina,OLD.rga_prof,NEW.cod_disciplina,NEW.rga_prof);
		RETURN NEW; 
    ELSIF TG_OP = 'DELETE' THEN
        tipo:='D';
		INSERT INTO disciplinalog VALUES (LOCALTIMESTAMP,tipo,OLD.cod_disciplina,OLD.rga_prof,NEW.cod_disciplina,NEW.rga_prof);
		RETURN OLD; 
    END IF;
END;
$$ LANGUAGE PLPGSQL;

CREATE TRIGGER disciplinalog BEFORE DELETE OR UPDATE OF cod_disciplina,rga_prof ON disciplina FOR EACH ROW EXECUTE PROCEDURE disciplinalog();

--logs de curso
CREATE OR REPLACE FUNCTION cursolog() RETURNS TRIGGER AS $$
DECLARE
    tipo char(1);
BEGIN
    IF TG_OP = 'UPDATE' THEN
        tipo:='U';
		INSERT INTO cursolog VALUES (LOCALTIMESTAMP,tipo,OLD.rga_coord,OLD.cod_curso,NEW.rga_coord,NEW.cod_curso);
		RETURN NEW;   
    ELSIF TG_OP = 'DELETE' THEN
        tipo:='D';
		INSERT INTO cursolog VALUES (LOCALTIMESTAMP,tipo,OLD.rga_coord,OLD.cod_curso,NEW.rga_coord,NEW.cod_curso);
		RETURN OLD;   
    END IF;          
END;
$$ LANGUAGE PLPGSQL;

CREATE TRIGGER cursolog BEFORE DELETE OR UPDATE OF cod_curso,rga_coord ON curso FOR EACH ROW EXECUTE PROCEDURE cursolog();

--logs de alunodisc
CREATE OR REPLACE FUNCTION alunodisclog() RETURNS TRIGGER AS $$
DECLARE
    tipo char(1);
BEGIN
    IF TG_OP = 'UPDATE' THEN
        tipo:='U';
		INSERT INTO alunodisclog VALUES (LOCALTIMESTAMP,tipo,OLD.rga_aluno,OLD.cod_disciplina,NEW.rga_aluno,NEW.cod_disciplina);
		RETURN NEW; 
    ELSIF TG_OP = 'DELETE' THEN
			tipo:='D';
		INSERT INTO alunodisclog VALUES (LOCALTIMESTAMP,tipo,OLD.rga_aluno,OLD.cod_disciplina,NEW.rga_aluno,NEW.cod_disciplina);
		RETURN OLD; 
    END IF;           
END;
$$ LANGUAGE PLPGSQL;

CREATE TRIGGER alunodisclog BEFORE DELETE OR UPDATE OF rga_aluno,cod_disciplina ON alunodisc FOR EACH ROW EXECUTE PROCEDURE alunodisclog();

--atualizar CR do aluno

CREATE OR REPLACE FUNCTION atualizacr() RETURNS TRIGGER AS $$
DECLARE
    cofrend DECIMAL;
BEGIN
    cofrend := (SELECT ROUND(AVG(t.notas),2) FROM (SELECT (nota1+nota2+nota3)/3 as notas FROM alunodisc WHERE alunodisc.rga_aluno=NEW.rga_aluno) as t);
    UPDATE aluno SET cr = cofrend WHERE rga_aluno=NEW.rga_aluno;
    RETURN NEW;
END;
$$ LANGUAGE PLPGSQL;

CREATE TRIGGER atualizacr AFTER UPDATE OF nota1,nota2,nota3 ON alunodisc FOR EACH ROW EXECUTE PROCEDURE atualizacr();