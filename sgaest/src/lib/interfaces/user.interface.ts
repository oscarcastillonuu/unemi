export interface Token {
	refresh?: string;
	access?: string;
}

export interface Seccion {
	id?: string;
	nombre?: string;
	imagen?: string;
}

export interface Modalidad {
	id?: string;
	nombre?: string;
	tipo?: number;
}

export interface Inscripcion {
	id?: string;
	seccion?: Seccion;
	modalidad?: Modalidad;
	isGraduado?: boolean;
	isEgresado?: boolean;
}

export interface Matricula {
	id?: string;
}

export interface Perfiles {
	id?: string;
	carrera?: string;
	clasificacion?: string;
	display_clasificacion?: string;
}

export interface PerfilPrincipal {
	id?: string;
}

export interface Periodo {
	id?: string;
	nombre_completo?: string;
}

export interface Periodos {
	id?: string;
	nombre_completo?: string;
}

export interface Persona {
	id?: string;
	tipo_documento?: string;
	documento?: string;
	apellido_materno?: string;
	apellido_paterno?: string;
	nombres?: string;
	nombre_completo?: string;
	nombre_minus?: string;
	correo_institucional?: string;
	correo_persona?: string;
	ciudad?: string;
	direccion?: string;
	foto?: string;
	sexo_id?: number;
}

export interface User {
	username?: string;
}

export interface Coordinacion {
	id?: string;
	nombre?: string;
	alias?: string;
	clasificacion?: number;
	display_clasificacion?: string;
}

export interface TemplateBaseSetting {
	name_system?: string;
	app?: boolean;
	use_menu_favorite_module?: boolean;
	use_menu_notification?: boolean;
	use_menu_user_manual?: boolean;
	use_api?: boolean;
}

export interface WebSocket {
	id?: string;
	url?: string;
	token?: string;
	observacion?: string;
	habilitado?: boolean;
	sga?: boolean;
	sagest?: boolean;
	posgrado?: boolean;
	postulacionposgrado?: boolean;
	api?: boolean;
}

export interface UserResponse {
	tokens?: Token;
	user?: User;
	inscripcion?: Inscripcion;
	matricula?: Matricula;
	perfiles?: Array<Perfiles>;
	perfilprincipal?: PerfilPrincipal;
	periodo?: Periodo;
	periodos?: Array<Periodos>;
	persona?: Persona;
	coordinacion?: Coordinacion;
	app?: string;
	connectionToken?: string;
	templatebasesetting?: TemplateBaseSetting;
	websocket?: WebSocket;
}
