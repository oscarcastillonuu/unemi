<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';
	export const load: Load = async ({ fetch }) => {
		
		let ePersona = {};						
		let eMatricula = {};			
		let estado_civil = [];
		let instituciones = [];
	
		const ds = browserGet('dataSession');
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			const [res, errors] = await apiGET(fetch, 'alumno/actualizadatos', {});			
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				return {
					status: 302,
					redirect: '/'
				};
			} else {
				if (!res.isSuccess) {
					if (!res.module_access) {
						if (res.redirect) {
							if (res.token) {
								//console.log(res.redirect);
								return (window.location.href = `${connectionToken}&ret=/${res.redirect}`);
							} else {
								addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
								return {
									status: 302,
									redirect: `/${res.redirect}`
								};
							}
						} else {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
							return {
								status: 302,
								redirect: '/'
							};
						}
					} else {
						addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					}
				} else {
					// console.log(res.data);										
					ePersona = res.data['ePersona'];
					instituciones = res.data['eInstitucionEducacionSuperior'];						
					eMatricula = res.data['eMatricula'];												
					estado_civil = res.data['estado_civil'];				
				}
			}
		}

		return {
			props: {								
				ePersona,
				instituciones,			
				eMatricula,							
				estado_civil				
			}
		};
	};
</script>

<script lang="ts">
	import { variables } from '$lib/utils/constants';
	import { addToast } from '$lib/store/toastStore';
    import { browserGet,apiPOSTFormData, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import { Button, Icon, Modal, ModalBody, ModalFooter, ModalHeader } from 'sveltestrap';
	import FilePond, { registerPlugin, supported } from 'svelte-filepond';
	import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
	import { onMount } from 'svelte';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { navigating } from '$app/stores';
	import ModalGenerico from '$components/Alumno/Modal.svelte';	
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import { addNotification } from '$lib/store/notificationStore';
	import { Spinner, Tooltip } from 'sveltestrap';
	import Swal from 'sweetalert2';
	import { goto } from '$app/navigation';
	import { createEventDispatcher, onDestroy } from 'svelte';
	import { dndzone, overrideItemIdKeyNameBeforeInitialisingDndZones } from 'svelte-dnd-action';
	//import MultiSelect from './_multiselect.svelte';
	import Select from 'svelte-select';
	import Item from './_selectAsync.svelte';
	import FormSelectSearch from '$components/Formulario/SelectSearch.svelte';
	import { getTitulos } from '$lib/utils/loadDataApi';
	import {aData} from "../alu_tematitulacionposgrado/_formagregartema.svelte";
    const dispatch = createEventDispatcher();
	export let ePersona;
	export let eMatricula;	
	export let estado_civil;	
	export let instituciones;	

	let load = true;	
	let itemsBreadCrumb = [{ text: 'Actualizar Datos', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };
	let aDataModal = {};
	let modalTitle = '';
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);	

	//campos validar solo numeros
	let valor = 0;
	let previusValue = 0.00;		

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	
	//Datos personales
	let dtpersona;
	let sexo=0;		
	let estadocivil_id = '';
	let lgtbi = false;					
	//Formulario datos personales
	let mSizeDatosPersonales = 'lg';
	let mOpenDatosPersonales = false;
	const mToggleDatosPersonales = () => (mOpenDatosPersonales = !mOpenDatosPersonales);
	let titleDatosPersonales;	

	//Datos nacimiento
	let dnpersona;
	let pais_nacimiento = [];
	let selected_pais_nacimiento ='';
	let nacionalidad ='';
	let provincia_nacimiento = [];
	let selected_provincia_nacimiento ='';
	let canton_nacimiento = [];
	let selected_canton_nacimiento = '';
	let parroquia_nacimiento = [];
	let selected_parroquia_nacimiento = '';
	//Formulario datos nacimiento
	let mSizeDatosNacimiento = 'lg';
	let mOpenDatosNacimiento = false;
	const mToggleDatosNacimiento = () => (mOpenDatosNacimiento = !mOpenDatosNacimiento);
	let titleDatosNacimiento;

	//Datos domicilio
	let ddpersona;
	let pais_residencia = [];
	let selected_pais_residencia ='';	
	let provincia_residencia = [];
	let selected_provincia_residencia ='';
	let canton_residencia = [];
	let selected_canton_residencia = '';
	let parroquia_residencia = [];
	let selected_parroquia_residencia = '';	
	let direccion_residencia = '';
	let direccion2_residencia = '';
	let num_direccion_residencia = '';
	let referencia_residencia = '';
	let telefono_conv_residencia = '';
	let telefono_residencia = '';
	//Formulario datos domicilio
	let mSizeDatosResidencia = 'lg';
	let mOpenDatosResidencia = false;
	const mToggleDatosResidencia = () => (mOpenDatosResidencia = !mOpenDatosResidencia);
	let titleDatosResidencia;

	//Datos etnia
	let depersona;
	let perfilinscripcion;	
	let razas = [];
	let selected_raza ='';	
	let nacionalidadesindigena = [];
	let selected_nacionalidadindigena = '';				
	//Formulario datos etnia
	let mSizeDatosEtnia = 'lg';
	let mOpenDatosEtnia = false;
	const mToggleDatosEtnia = () => (mOpenDatosEtnia = !mOpenDatosEtnia);
	let titleDatosEtnia;	

	//Datos Titulacion
	let dtitulacionpersona;
	let titulacion;	
	let titulacion_id='';	
	let titulo = [];
	let institucion = [];	
	let titulo_id =0;
	let selected_titulo = null;	
	let selected_institucion = null;	
	let institucion_id = '';
	
	let tituloArchivo = '';
	let tituloSenescyt = '';
	let tituloregistro = '';
	let pondTitulo;
	let pondSenescyt;
	let nameTitulo = 'fileTitulo';	
	let nameSenescyt = 'fileSenescyt';
	const getOptionLabel = (option) => option.display;
	const getSelectionLabel = (option) => option.display;	

	//Formulario datos Titulacion
	let mSizeDatosTitulacion = 'lg';
	let mOpenDatosTitulacion = false;
	const mToggleDatosTitulacion = () => (mOpenDatosTitulacion = !mOpenDatosTitulacion);
	let titleDatosTitulacion;	

	onMount(async () => {
		registerPlugin(FilePondPluginFileValidateType);
		const ds = browserGet('dataSession');
		const dataSession = JSON.parse(ds);
		const coordinacion = dataSession['coordinacion'];		
		//clasificacion = coordinacion.clasificacion;
		if (ePersona){
			load = false;
		}
	
	});

	// handle filepond events
	const handleInit = () => {
		console.log('FilePond has initialised');
	};

	const handleAddFile = (err, fileItem) => {
		console.log(pondTitulo.getFiles());
		console.log('A file has been added', fileItem);
	};

	const limpiarcampos = () => {		
		selected_pais_nacimiento ='';				
		selected_provincia_nacimiento ='';		
		selected_canton_nacimiento = '';		
		selected_parroquia_nacimiento = '';
		selected_pais_residencia ='';				
		selected_provincia_residencia ='';		
		selected_canton_residencia = '';		
		selected_parroquia_residencia = '';	
		direccion_residencia = '';
	    direccion2_residencia = '';	
	};	

	function soloNumeros(node, value) {
		return {
			update(value) {
				valor =
					value === null || valor < node.min ? previusValue : parseFloat(value);
				previusValue = 0.00;
			}
		};
	}

	function padTo2Digits(num) {
		return num.toString().padStart(2, '0');
	}

	function formatDate(date) {
		return [
			date.getFullYear(),
			padTo2Digits(date.getMonth() + 1),
			padTo2Digits(date.getDate())
		].join('-');
	}

	const openDatosPersonales = async () => {		
		loading.setLoading(false, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/actualizadatos', {
			action: 'datospersonales'
		});
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {		
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {								
				dtpersona = res.data['ePersona'];	
				sexo = dtpersona.sexo
				if (dtpersona.estado_civil){
					estadocivil_id=dtpersona.estado_civil
				}									
				if (dtpersona.lgtbi){
					lgtbi = true;	
				}else{
					lgtbi = false;
				}
								
			}
		}
		mSizeDatosPersonales = 'lg';
		mOpenDatosPersonales = true;
		titleDatosPersonales = 'Datos Personales';
	};

	const closeDatosPersonalesForm = () => {
		mOpenDatosPersonales = false;
	};	

	const saveDatosPersonales = async (id = null) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmDatosPersonales = document.querySelector('#frmDatosPersonales');
		const formData = new FormData($frmDatosPersonales);
		const numeros = /^([0-9])*$/;
		
		formData.append('action', 'actualizardatospersonales');
		formData.append('id_matri', eMatricula.id);
		formData.append('id_persona', id);		

		let nombres = document.getElementById('eNombres');		
		let apellido1 = document.getElementById('eApellido1');
		let apellido2 = document.getElementById('eApellido2');
		let cedula = document.getElementById('eCedula');		
		let sexo = document.getElementById('eSexo');		
		let estadocivil_ = document.getElementById('eEstadoCivil');
		let fechanacimiento = document.getElementById('eFechaNacimiento');		
		let correopersonal = document.getElementById('eCorreoPersonal');
		let correoinstitucional = document.getElementById('eCorreoInstitucional');		
				
		formData.append('eLgtbi', lgtbi);
		if (!nombres.value) {
			addNotification({
				msg: 'Favor complete el campo de nombres',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (!apellido1.value) {
			addNotification({
				msg: 'Favor complete el campo de apellido 1',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} 
		if (!apellido2.value) {
			addNotification({
				msg: 'Favor complete el campo de apellido 2',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (!cedula.value) {
			addNotification({
				msg: 'Favor complete el campo de cédula',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}		
		if (!cedula.value.match(numeros)) {
			addNotification({
				msg: 'Célula incorrecta',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (
			sexo.value === null ||
			sexo.value === undefined ||
			sexo.value === '' ||
			sexo.value === '0'
		) {
			addNotification({
				msg: 'Seleccione su sexo',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('sexo', sexo.value);
		}
		if (
			estadocivil_.value === null ||
			estadocivil_.value === undefined ||
			estadocivil_.value === '' ||
			estadocivil_.value === '0'
		) {
			addNotification({
				msg: 'Seleccione su estado civil',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('estadocivil', estadocivil_.value);			
		}
		if (!fechanacimiento.value) {
			addNotification({
				msg: 'Favor complete el campo de fecha de nacimiento',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (!correopersonal.value) {
			addNotification({
				msg: 'Favor complete el campo de correo electrónico personal',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (!correoinstitucional.value) {
			addNotification({
				msg: 'Favor complete el campo de correo electrónico Institucional',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}		
		
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/actualizadatos', formData);
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/alu_actualizadatos');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
				mOpenDatosPersonales = false;				
				location.reload();
			}
		}
	};

	const openDatosNacimiento = async () => {		
		limpiarcampos();
		loading.setLoading(false, 'Cargando, espere por favor...');		
		const [res, errors] = await apiPOST(fetch, 'alumno/actualizadatos', {
			action: 'datospersonales', nacimiento:true
		});
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {								
				dnpersona = res.data['ePersona'];
				pais_nacimiento = res.data['ePais'];
				provincia_nacimiento = res.data['eProvincia'];
				canton_nacimiento = res.data['eCanton'];
				parroquia_nacimiento = res.data['eParroquia'];
				
				if (dnpersona.paisnacimiento){
					selected_pais_nacimiento = dnpersona.paisnacimiento;					
				}
				if (dnpersona.provincianacimiento){
					selected_provincia_nacimiento = dnpersona.provincianacimiento;
				}
				if (dnpersona.cantonnacimiento){
					selected_canton_nacimiento = dnpersona.cantonnacimiento;
				}
				if (dnpersona.parroquianacimiento){
					selected_parroquia_nacimiento = dnpersona.parroquianacimiento;
				}																					
				nacionalidad = dnpersona.nacionalidad;																		
			}
		}
		mSizeDatosNacimiento = 'lg';
		mOpenDatosNacimiento = true;
		titleDatosNacimiento = 'Datos de Nacimiento';
	};

	const closeDatosNacimientoForm = () => {
		mOpenDatosNacimiento = false;
	};

	const saveDatosNacimiento = async (id = null) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmDatosNacimiento = document.querySelector('#frmDatosNacimiento');
		const formData = new FormData($frmDatosNacimiento);		
		
		formData.append('action', 'actualizardatosnacimiento');
		formData.append('id_matri', eMatricula.id);
		formData.append('id_persona', id);		
			
		let nacionalidad = document.getElementById('eNacionalidad');					
							
		if (
			selected_pais_nacimiento === '' ||
			selected_pais_nacimiento === null ||
			selected_pais_nacimiento === undefined
		) {
			addNotification({
				msg: 'Seleccione un pais',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('pais', selected_pais_nacimiento.idm);
		}
		if (
			selected_provincia_nacimiento === '' ||
			selected_provincia_nacimiento === null ||
			selected_provincia_nacimiento === undefined
		) {
			addNotification({
				msg: 'Seleccione una provincia',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('provincia', selected_provincia_nacimiento.idm);			
		}
		if (
			selected_canton_nacimiento === '' ||
			selected_canton_nacimiento === null ||
			selected_canton_nacimiento === undefined
		) {
			addNotification({
				msg: 'Seleccione un cantón',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('canton', selected_canton_nacimiento.idm);
		}
		if (
			selected_parroquia_nacimiento === '' ||
			selected_parroquia_nacimiento === null ||
			selected_parroquia_nacimiento === undefined
		) {
			addNotification({
				msg: 'Seleccione una parroquia',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('parroquia', selected_parroquia_nacimiento.idm);			
		}			
		if (!nacionalidad.value) {
			addNotification({
				msg: 'Favor complete el campo de Nacionalidad',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}	
		
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/actualizadatos', formData);
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/alu_actualizadatos');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
				mOpenDatosNacimiento = false;				
				location.reload();
			}
		}
	};	

	const handeChangePais = async (id, dato) => {
		loading.setLoading(false, 'Cargando, espere por favor...');	
		console.log(id);				
		const [res, errors] = await apiPOST(fetch, 'alumno/actualizadatos', {
			action: 'filtra_provincia', id: id
		});
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {	
				if (dato === 'domicilio'){
					provincia_residencia = res.data['eProvincia'];										
					canton_residencia = [];
					parroquia_residencia = [];
					selected_provincia_residencia='';
					selected_canton_residencia='';
					selected_parroquia_residencia='';		
				}

				if (dato === 'nacimiento'){
					provincia_nacimiento = res.data['eProvincia'];				
					nacionalidad = res.data['eNacionalidad'];	
					canton_nacimiento = [];
					parroquia_nacimiento = [];	
					selected_provincia_nacimiento ='';
					selected_canton_nacimiento ='';
					selected_parroquia_nacimiento ='';		
				}											
																										
			}
		}
	}
	const handeChangeProvincia = async (id, dato) => {
		loading.setLoading(false, 'Cargando, espere por favor...');		
		const [res, errors] = await apiPOST(fetch, 'alumno/actualizadatos', {
			action: 'filtra_canton', id: id
		});
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {
				if (dato === 'domicilio'){
					canton_residencia = res.data['eCanton'];
					parroquia_residencia = [];																				
					selected_canton_residencia='';
					selected_parroquia_residencia='';	
				}

				if (dato === 'nacimiento'){
					canton_nacimiento = res.data['eCanton'];
					parroquia_nacimiento = [];
					selected_canton_nacimiento ='';
					selected_parroquia_nacimiento ='';
				}																				
			}
		}
	}
	const handeChangeCanton = async (id, dato) => {
		loading.setLoading(false, 'Cargando, espere por favor...');		
		const [res, errors] = await apiPOST(fetch, 'alumno/actualizadatos', {
			action: 'filtra_parroquia', id: id
		});
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {		
				if (dato === 'domicilio'){
					parroquia_residencia = res.data['eParroquia'];	
					selected_parroquia_residencia='';		
				}

				if (dato === 'nacimiento'){
					parroquia_nacimiento = res.data['eParroquia'];						
					selected_parroquia_nacimiento ='';				
				}																															
			}
		}
	}

	function changepaisnacimiento(event) {		
		handeChangePais(event.detail.value,'nacimiento')
	}
	function changepaisdomicilio(event) {		
		handeChangePais(event.detail.value,'domicilio')
	}
	function changeprovincianacimiento(event) {		
		handeChangeProvincia(event.detail.value,'nacimiento')
	}
	function changeprovinciadomicilio(event) {		
		handeChangeProvincia(event.detail.value,'domicilio')
	}
	function changecantonnacimiento(event) {		
		handeChangeCanton(event.detail.value,'nacimiento')
	}
	function changecantondomicilio(event) {		
		handeChangeCanton(event.detail.value,'domicilio')
	}

	const openDatosResidencia = async () => {	
		limpiarcampos();	
		loading.setLoading(false, 'Cargando, espere por favor...');		
		const [res, errors] = await apiPOST(fetch, 'alumno/actualizadatos', {
			action: 'datospersonales', domicilio:true
		});
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {																		

				ddpersona = res.data['ePersona'];
				pais_residencia = res.data['ePais'];
				provincia_residencia = res.data['eProvincia'];
				canton_residencia = res.data['eCanton'];
				parroquia_residencia = res.data['eParroquia'];
				
				if (ddpersona.pais){
					selected_pais_residencia = ddpersona.pais;	
				}
				if (ddpersona.provincia){
					selected_provincia_residencia = ddpersona.provincia;	
				}
				if (ddpersona.canton){
					selected_canton_residencia = ddpersona.canton;
				}
				if (ddpersona.parroquia){
					selected_parroquia_residencia = ddpersona.parroquia;
				}
				if (ddpersona.direccion){
					direccion_residencia = ddpersona.direccion;
				}
				if (ddpersona.direccion2){
					direccion2_residencia = ddpersona.direccion2;
				}
				if (ddpersona.num_direccion){
					num_direccion_residencia = ddpersona.num_direccion;
				}
				if (ddpersona.referencia){
					referencia_residencia = ddpersona.referencia;
				}
				if (ddpersona.telefono_conv){
					telefono_conv_residencia = ddpersona.telefono_conv;
				}
				if (ddpersona.telefono){
					telefono_residencia = ddpersona.telefono;
				}
																																											
			}
		}
		mSizeDatosResidencia = 'lg';
		mOpenDatosResidencia = true;
		titleDatosResidencia = 'Datos de Domicilio  | Residencia actual';
	};

	const closeDatosResidenciaForm = () => {
		mOpenDatosResidencia = false;
	};

	const saveDatosResidencia = async (id = null) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmDatosResidencia = document.querySelector('#frmDatosResidencia');
		const formData = new FormData($frmDatosResidencia);		
		const numeros = /^([0-9])*$/;
		
		formData.append('action', 'actualizardatosdomicilio');
		formData.append('id_matri', eMatricula.id);
		formData.append('id_persona', id);		
			
		let calle_principal = document.getElementById('eCallePrincipal');			
		let celular = document.getElementById('eCelular');				
									
		if (
			selected_pais_residencia === '' ||
			selected_pais_residencia === null ||
			selected_pais_residencia === undefined
		) {
			addNotification({
				msg: 'Seleccione un pais',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('pais', selected_pais_residencia.idm);
		}
		if (
			selected_provincia_residencia === '' ||
			selected_provincia_residencia === null ||
			selected_provincia_residencia === undefined
		) {
			addNotification({
				msg: 'Seleccione una provincia',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('provincia', selected_provincia_residencia.idm);			
		}
		if (
			selected_canton_residencia === '' ||
			selected_canton_residencia === null ||
			selected_canton_residencia === undefined
		) {
			addNotification({
				msg: 'Seleccione un cantón',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('canton', selected_canton_residencia.idm);
		}
		if (
			selected_parroquia_residencia === '' ||
			selected_parroquia_residencia === null ||
			selected_parroquia_residencia === undefined
		) {
			addNotification({
				msg: 'Seleccione una parroquia',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('parroquia', selected_parroquia_residencia.idm);			
		}	
		
		if (!calle_principal.value) {
			addNotification({
				msg: 'Favor complete el campo de calle principal',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}			
		if (!celular.value) {
			addNotification({
				msg: 'Favor complete el campo de celular',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}	
		if (!celular.value.match(numeros)) {
			addNotification({
				msg: 'Celular incorrecto',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}		
		
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/actualizadatos', formData);
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/alu_actualizadatos');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
				mOpenDatosResidencia = false;				
				location.reload();
			}
		}
	};

	const openDatosEtnia = async () => {		
		loading.setLoading(false, 'Cargando, espere por favor...');
		selected_raza ='';
		selected_nacionalidadindigena ='';
		const [res, errors] = await apiPOST(fetch, 'alumno/actualizadatos', {
			action: 'datosetnia'
		});
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
			
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {								
				depersona = res.data['ePersona'];
				perfilinscripcion = res.data['ePerfilInscripcion'];
				razas = res.data['eRazas'];
				nacionalidadesindigena = res.data['eNacionalidadIndigenas'];
				if (perfilinscripcion.raza){
					selected_raza = perfilinscripcion.raza;
				}				
				if (perfilinscripcion.nacionalidadindigena){
					selected_nacionalidadindigena = perfilinscripcion.nacionalidadindigena;
				}																
			}
		}
		mSizeDatosEtnia = 'lg';
		mOpenDatosEtnia = true;
		titleDatosEtnia = 'Etnia';
	};

	const closeDatosEtniaForm = () => {
		mOpenDatosEtnia = false;
	};	

	const saveDatosEtnia = async (id = null) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmDatosEtnia = document.querySelector('#frmDatosEtnia');
		const formData = new FormData($frmDatosEtnia);		
		
		formData.append('action', 'actualizardatosetnia');
		formData.append('id_matri', eMatricula.id);
		formData.append('id_perfilinscripcion', id);		

		if (
			selected_raza === '' ||
			selected_raza === null ||
			selected_raza === undefined
		) {
			addNotification({
				msg: 'Seleccione un Etnia',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('raza', selected_raza.idm);
		}
		if (
			selected_nacionalidadindigena
		) {	
			formData.append('nacionalidadindigena', selected_nacionalidadindigena.idm);
		}					
		
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/actualizadatos', formData);
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/alu_actualizadatos');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
				mOpenDatosEtnia = false;				
				location.reload();
			}
		}
	};

	const loadOptions  = async (filterText) => {
		const [res, errors] = await apiGET(fetch, 'alumno/actualizadatos', {
			action: 'buscartitulos',
			//periodo_id: periodo_id,
			//carrera_id: carrera_id,
			filterText: filterText
		});
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {				
				return new Promise((resolve) => {
					setTimeout(resolve(res.data.items.sort((a, b) => {
          						if (a.display > b.display) return 1;
          						if (a.display < b.display) return -1;
        			})), 2000);					
				});	
										
			}
		}
	
	}

	const openDatosTitulacion = async (id='') => {			
		loading.setLoading(false, 'Cargando, espere por favor...');
		console.log('id');
		console.log(id);
		if (id){	
			const [res, errors] = await apiPOST(fetch, 'alumno/actualizadatos', {
				action: 'datostitulacion', idtitulacion :id
			});
			if (errors.length > 0) {
				addNotification({
					msg: errors[0].error,
					type: 'error'
				});
			} else {
				if (!res.isSuccess) {				
					addNotification({
						msg: res.message,
						type: 'error'
					});
				} else {											
					dtitulacionpersona = res.data['ePersona'];
					titulacion = res.data['eTitulacion'];
					titulo = res.data['eTitulo'];
					institucion = res.data['eInstitucion'];								
					titulacion_id = titulacion.id;
					if (titulacion.titulo){
						titulo_id = titulacion.titulo;
						selected_titulo = {
							id: titulo['idm'],
							name: titulo['display']
						}
						selected_institucion = institucion;
					}				
					if (titulacion.institucion){
						institucion_id = titulacion.institucion;
					}
					if (titulacion.archivo){
						tituloArchivo = titulacion.archivo;
					}
					if (titulacion.registroarchivo){
						tituloSenescyt = titulacion.registroarchivo;
					}
					if (titulacion.registro){
						tituloregistro = titulacion.registro;
					}																							
				}
			}
		}else{
			titulacion = null;
			titulacion_id ='';
			selected_titulo = null;
			selected_institucion = null;
			institucion_id = '';
			tituloregistro = '';
			tituloSenescyt = '';
			tituloArchivo = '';
		}
		mSizeDatosTitulacion = 'lg';
		mOpenDatosTitulacion = true;
		titleDatosTitulacion = 'Titulacion | Tercer Nivel';
	};

	const closeDatosTitulacionForm = () => {
		mOpenDatosTitulacion = false;
	};

	const saveDatosTitulacion = async (id = null) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmDatosTitulacion = document.querySelector('#frmDatosTitulacion');
		const formData = new FormData($frmDatosTitulacion);		
		
		formData.append('action', 'actualizardatostitulacion');
		formData.append('id_matri', eMatricula.id);
		formData.append('id_titulacion', id);		

		let titulo = document.getElementById('eTitulo');		
		let institucion = document.getElementById('eInstitucionEdu');	
		let numregistro = document.getElementById('eNumRegistro');		
				
		if (
			selected_titulo === null||
			selected_titulo === undefined
		) {
			addNotification({
				msg: 'Seleccione un Título',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('titulo', selected_titulo.id);
		}
		if (
			selected_institucion === null ||
			selected_institucion === undefined
		) {
			addNotification({
				msg: 'Seleccione una Institución Educativa',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('institucion', selected_institucion.id);			
		}	
				
		if (!numregistro.value) {
			addNotification({
				msg: 'Favor complete el campo de N° de registro SENESCYT',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		
		if(tituloArchivo == ''){		
			let fileTitulo = pondTitulo.getFiles();
			if (fileTitulo.length == 0) {
				addNotification({
					msg: 'Debe subir archivo de documento del Título',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (fileTitulo.length > 1) {
				addNotification({
					msg: 'Archivo de documento del Título debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
		}

		let eFileTitulo = undefined;
		if (pondTitulo && pondTitulo.getFiles().length > 0) {
			eFileTitulo = pondTitulo.getFiles()[0];
		}
		console.log('eFileTitulo');
		console.log(eFileTitulo);
		if(eFileTitulo){
			formData.append('fileTitulo', eFileTitulo.file);
		}		
		
		if(tituloSenescyt){		
			let fileSenescyt = pondSenescyt.getFiles();			
			if (fileSenescyt.length > 1) {
				addNotification({
					msg: 'Archivo de documento de Senescyt debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
		}

		let eFileSenescyt = undefined;
		if (pondSenescyt && pondSenescyt.getFiles().length > 0) {
			eFileSenescyt = pondSenescyt.getFiles()[0];
		}
		
		if(eFileSenescyt){
			formData.append('fileSenescyt', eFileSenescyt.file);
		}
				
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/actualizadatos', formData);
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/alu_actualizadatos');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
				mOpenDatosTitulacion = false;				
				location.reload();
			}
		}
	};

	const eliminarTitulacion = async (eTitulacion) => {		
		const mensaje = {
			title: `NOTIFICACIÓN`,
			text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, con esta acción usted eliminará el registro: ${eTitulacion.nombre}. ¿Está ${
				ePersona.es_mujer ? 'segura' : 'seguro'
			} de eliminar su titulación?`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#FE9900',			
			confirmButtonText: 'Si, seguro',
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje)
			.then(async (result) => {
				if (result.value) {
					loading.setLoading(true, 'Eliminando, espere por favor...');
					const [res, errors] = await apiPOST(fetch, 'alumno/actualizadatos', {
						action: 'deletetitulacion',
						id: eTitulacion.id
					});
					loading.setLoading(false, 'Eliminando, espere por favor...');
					if (errors.length > 0) {
						addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
						goto('/alu_actualizadatos');
					} else {
						if (!res.isSuccess) {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
						} else {
							addToast({
								type: 'success',
								header: 'Exitoso',
								body: 'Se eliminó correctamente la titulación'
							});							
							loading.setLoading(false, 'Cargando, espere por favor...');
							location.reload();
						}
					}
				} else {
					addToast({
						type: 'info',
						header: 'Enhorabuena',
						body: 'Has cancelado la acción de eliminar titulación'
					});
				}
			})
			.catch((error) => {
				addToast({ type: 'error', header: 'Ocurrio un error', body: error });
			});
	};	

	const loadConfirmacionDatos  = async () => {		
		const [res, errors] = await apiGET(fetch, 'alumno/actualizadatos', {
			action: 'confirmacion_datos',			
			id_matri: eMatricula.id		    
		});
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				if (!res.module_access) {
					if (res.redirect) {
						if (res.token) {								
							addToast({ type: 'success', header: 'Exitoso', body: 'Sus datos personales han sido actualizados correctamente.' });						
							goto('/');
						} else {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });							
							return;
						}
					} else {
						addNotification({
							msg: res.message,
							type: 'warning',
							target: 'newNotificationToast'
						});						
					}					
				} else {
					addNotification({
						msg: res.message,
						type: 'warning',
						target: 'newNotificationToast'
					});						
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;										
			}
		}
	
	}
	
	const changeTitulo = (event) => {
		//console.log("change: ", event);
	};

</script>

<svelte:head>
	<title>Actualizar Datos</title>
</svelte:head>

{#if !load}
<BreadCrumb title="Actualizar Datos" items={itemsBreadCrumb} back={backBreadCrumb} />
	<div class="row">
		<div class="col-12">
			<div class="card mb-4">
				<!-- Card header -->
				<div class="card-header">
					<h3 class="mb-0">Datos personales</h3>					
				</div>
				<div class="card-header">					
					<div class="dropdown">													
						<div class="card-header">
							<div class="alert alert-danger d-flex align-items-center" role="alert">
								<svg
									xmlns="http://www.w3.org/2000/svg"
									width="24"
									height="24"
									fill="currentColor"
									class="bi bi-info-circle-fill me-2"
									viewBox="0 0 16 16"
								>
									<path
										d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"
									/>
								</svg>
								<div>
									{#if ePersona.sexo_id == 1 }Estimada{:else}Estimado{/if}, por temas de Titulación, es necesario que se encuentren actualizados todos sus datos personales y su formación académica. Por favor revise, corrija y actualize su información personal. Al finalizar de click en el boton <strong>Confirmar</strong>	para terminar el proceso.								
								</div>
							</div>
						</div>	
						<h4 class="mb-0">Maestrante: {ePersona.nombres} {ePersona.apellido1} {ePersona.apellido2}</h4>
						{#if eMatricula }<h4 class="mb-0">Carrera: {eMatricula.carrera.nombre_completo} </h4>{/if}																												
					</div>					  					
				</div>
				<!-- Card body -->
				<div class="card-body">										
					<div class="table-responsive">
						<!--border-0 table-invoice-->
						<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
							<thead class="table-light">
								<tr>
									<th colspan="4" scope="col" class="border-top-0">DATOS PERSONALES 										
										<button
											on:click={() => openDatosPersonales()}
											class="btn btn-warning btn-sm"
											style="float: right;"
										>
											<i class="bi bi-pencil-square" /> Editar/actualizar
										</button>																														
									</th>																																														
								</tr>
							</thead>
							<tbody>
								<tr>
									<td class="text-wrap fs-6">																				
										<strong>Nombres:</strong> {#if ePersona.nombres }{ePersona.nombres}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}																			
									</td>
									<td class="text-wrap fs-6">																				
										<strong>1er. Apellido:</strong> {#if ePersona.apellido1 }{ePersona.apellido1}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}																					
									</td>
									<td class="text-wrap fs-6">																				
										<strong>2er. Apellido:</strong> {#if ePersona.apellido2 }{ePersona.apellido2}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}																	
									</td>
									<td class="text-wrap fs-6">																				
										<strong>Fecha de nacimiento:</strong> {#if ePersona.nacimiento }{ePersona.nacimiento}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}												
									</td>																																		
								</tr>
								<tr>
									
									<td class="text-wrap fs-6">																				
										<strong>Cédula:</strong> {#if ePersona.cedula }{ePersona.cedula}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}															
									</td>
									<td class="text-wrap fs-6">																				
										<strong>Pasaporte:</strong> {#if ePersona.pasaporte }{ePersona.pasaporte}{:else}NO REGISTRA{/if}		
									</td>									
									<td class="text-wrap fs-6">																				
										<strong>Años de residencia:</strong> {#if ePersona.anioresidencia }{ePersona.anioresidencia}{:else}0{/if}	
									</td>
									<td class="text-wrap fs-6">																				
										<strong>Estado Civil:</strong> 	{#if ePersona.estado_civil_des }{ePersona.estado_civil_des}{:else}NO REGISTRA{/if}
									</td>																								
								</tr>	
								<tr>
									<td class="text-wrap fs-6">																				
										<strong>Sexo:</strong> {#if ePersona.sexo }{ePersona.sexo_des}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}
									</td>
									<td class="text-wrap fs-6">																														
										<strong>Pertenece al Grupo LGTBI ?</strong> {#if ePersona.lgtbi }SI{:else}NO{/if}																		
									</td>
									<td class="text-wrap fs-6">																				
										<strong>Correo:</strong> {#if ePersona.email }{ePersona.email}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}													
									</td>
									<td class="text-wrap fs-6">																				
										<strong>Libreta Militar:</strong> {#if ePersona.libretamilitar }{ePersona.libretamilitar}{:else}NO REGISTRA{/if}																				
									</td>																									
								</tr>																		
							</tbody>
						
						</table>
						
						<br>

						<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
							<thead class="table-light">
								<tr>
									<th colspan="4" scope="col" class="border-top-0">DATOS DE NACIMIENTO 
										<button
											on:click={() => openDatosNacimiento()}
											class="btn btn-warning btn-sm"
											style="float: right;"
										>
											<i class="bi bi-pencil-square" /> Editar/actualizar
										</button>	
									</th>																																														
								</tr>
							</thead>
							<tbody>
								<tr>
									<td class="text-wrap fs-6">																				
										<strong>País:</strong> {#if ePersona.paisnacimiento }{ePersona.paisnacimiento_des}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}																			
									</td>
									<td class="text-wrap fs-6">																				
										<strong>Provincia:</strong> {#if ePersona.provincianacimiento }{ePersona.provincianacimiento_des}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}																					
									</td>
									<td class="text-wrap fs-6">																				
										<strong>Cantón:</strong> {#if ePersona.cantonnacimiento }{ePersona.cantonnacimiento_des}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}																	
									</td>																																		
								</tr>
								<tr>									
									<td class="text-wrap fs-6">																				
										<strong>Parroquia:</strong> {#if ePersona.parroquianacimiento }{ePersona.parroquianacimiento_des}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}												
									</td>	
									<td class="text-wrap fs-6">																				
										<strong>Nacionalidad:</strong> {#if ePersona.nacionalidad }{ePersona.nacionalidad}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}
									</td>
									<td class="text-wrap fs-6">																														
									</td>																									
								</tr>
																																								
							</tbody>						
						</table>

						<br>

						<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
							<thead class="table-light">
								<tr>
									<th colspan="4" scope="col" class="border-top-0">DATOS DE DOMICILIO | RESIDENCIA ACTUAL
										<button
											on:click={() => openDatosResidencia()}
											class="btn btn-warning btn-sm"
											style="float: right;"
										>
											<i class="bi bi-pencil-square" /> Editar/actualizar
										</button>	
									</th>																																														
								</tr>
							</thead>
							<tbody>
								<tr>
									<td class="text-wrap fs-6">																				
										<strong>País:</strong> {#if ePersona.pais }{ePersona.pais_des}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}																			
									</td>
									<td class="text-wrap fs-6">																				
										<strong>Provincia:</strong> {#if ePersona.provincia }{ePersona.provincia_des}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}																					
									</td>
									<td class="text-wrap fs-6">																				
										<strong>Cantón:</strong> {#if ePersona.canton }{ePersona.canton_des}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}																	
									</td>
									<td class="text-wrap fs-6">																				
										<strong>Parroquia:</strong> {#if ePersona.parroquia }{ePersona.parroquia_des}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}												
									</td>																									
								</tr>	
								<tr>
									<td colspan="2" class="text-wrap fs-6">																				
										<strong>Calle Principal:</strong> 	{#if ePersona.direccion }{ePersona.direccion}{:else}NO REGISTRA{/if}
									</td>
									<td colspan="2" class="text-wrap fs-6">																				
										<strong>Calle Secundaria:</strong> {#if ePersona.direccion2 }{ePersona.direccion2}{:else}NO REGISTRA{/if}								
									</td>																																
								</tr>		
								<tr>
									<td class="text-wrap fs-6">																				
										<strong>Número(Domicilio):</strong> {#if ePersona.num_direccion }{ePersona.num_direccion}{:else}NO REGISTRA{/if}															
									</td>
									<td class="text-wrap fs-6">																				
										<strong>Referencia:</strong> {#if ePersona.referencia }{ePersona.referencia}{:else}NO REGISTRA{/if}		
									</td>
									<td class="text-wrap fs-6">																				
										<strong>Teléfono domicilio:</strong> {#if ePersona.telefono_conv }{ePersona.telefono_conv}{:else}NO REGISTRA{/if}
									</td>
									<td class="text-wrap fs-6">																				
										<strong>Celular:</strong> {#if ePersona.telefono }{ePersona.telefono}{:else}NO REGISTRA{/if}	
									</td>																								
								</tr>																										
							</tbody>						
						</table>
						<br>						
						<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
							<thead class="table-light">
								<tr>
									<th colspan="4" scope="col" class="border-top-0">ETNIA
										<button
											on:click={() => openDatosEtnia()}
											class="btn btn-warning btn-sm"
											style="float: right;"
										>
											<i class="bi bi-pencil-square" /> Editar/actualizar
										</button>	
									</th>																																														
								</tr>
							</thead>
							<tbody>
								<tr>									
									<td class="text-wrap fs-6">																				
										<strong>Etnia:</strong> {#if ePersona.perfil.raza }{ePersona.perfil.nombre_raza}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}																			
									</td>
									<td class="text-wrap fs-6">																				
										<strong>Nacionalidad Indígena:</strong> {#if ePersona.perfil.nacionalidadindigena }{ePersona.perfil.nombre_nacionalidadindigena}{:else}NO REGISTRA{/if}
									</td>																																	
								</tr>																									
							</tbody>						
						</table>

						<br>	

						<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
							<thead class="table-light">
								<tr>
									<th colspan="6" scope="col" class="border-top-0">TITULACIÓN | TERCER NIVEL
										<button
											on:click={() => openDatosTitulacion()}
												class="btn btn-success btn-sm"
												style="float: right;"
											>
												<i class="bi bi-file-earmark-plus-fill" /> Adicionar
											</button>											
									</th>																																														
								</tr>
								<tr style="text-align: center;">
									<th scope="col" class="border-top-0">Título</th>
									<th scope="col" class="border-top-0">Institución</th>
									<th scope="col" class="border-top-0">N° Registro SENESCYT</th>
									<th scope="col" class="border-top-0">Archivos</th>									
									<th scope="col" class="border-top-0">Acción</th>																																														
								</tr>
							</thead>
							<tbody>
								{#if ePersona.titulacion_tercernivel.length > 0}
									{#each ePersona.titulacion_tercernivel as titulo }																										
										<tr>									
											<td class="text-wrap fs-6">																		
												{#if titulo.nombre }{titulo.nombre}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}																			
											</td>
											<td class="text-wrap fs-6">																				
												{#if titulo.institucion_des }{titulo.institucion_des}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}																					
											</td>
											<td style="text-align: center ;" class="text-wrap fs-6">																				
												{#if titulo.registro }{titulo.registro}{:else}<span class="badge bg-danger">PENDIENTE</span>{/if}																					
											</td>	
											<td style="text-align: center ;" class="text-wrap fs-6">																															
												<strong><i class="bi bi-file-pdf text-success" /> Título</strong><br>
												{#if titulo.pdfarchivo }
													<a
														href="{titulo.pdfarchivo}"
														style="background-color: #2d8cff!important;"
														class="btn btn-info btn-sm"
														target="_blank"
													>
														<i class="bi bi-file-eye" /> Ver
													</a>												
												{:else}
													<span class="badge bg-danger">PENDIENTE</span>
												{/if}	<br>																		
												<strong><i class="bi bi-file-pdf text-success" /> Documento SENESCYT</strong><br>																												
												{#if titulo.pdfarchivosenecyt }
													<a
														href="{titulo.pdfarchivosenecyt}"
														style="background-color: #2d8cff!important;"
														class="btn btn-info btn-sm"
														target="_blank"
													>
														<i class="bi bi-eye" /> Ver
													</a>	
												
												{:else}
													NO REGISTRA
												{/if}																					
											</td>	
											<td style="text-align: center;">
												<button
													on:click={() => openDatosTitulacion(titulo.id)}
													class="btn btn-warning btn-sm"
													style="float: right;"
												>
													<i class="bi bi-pencil-square" /> Editar
												</button>
												<br><br>
												<button
													on:click={() => eliminarTitulacion(titulo)}
													class="btn btn-danger btn-sm"
													style="float: right;"
												>
													<i class="fe fe-trash-2" /> Eliminar
												</button>											
											</td>																															
										</tr>	
										
											
									{/each}	
								{:else}
									<tr>										
										<td colspan="8" class="text-center"
											><span class="badge bg-danger">NO EXISTEN REGISTRO DE TITULACIÓN </span>
										</td
										>
									</tr>
								{/if}
																															
							</tbody>						
						</table>
						<br>
					</div>
					
					<button
						on:click={() => loadConfirmacionDatos()}
							class="btn btn-success btn-sm"
							style="float: left;"
						>
							<i class="bi bi-journal-check" /> Confirmar
					</button>						
					
				</div>
			</div>
		</div>
	</div>
{:else}
	<div
		class="mt-4 vh-100 row justify-content-center align-items-center"
		style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center;"
	>
		<div class="col-auto text-center">
			<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
			<h3>Verificando la información, espere por favor...</h3>
		</div>
	</div>
{/if}

<Modal
	isOpen={mOpenDatosPersonales}
	toggle={mToggleDatosPersonales}
	size={mSizeDatosPersonales}
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
	backdrop="static"
	fade={false}
>
	<ModalHeader toggle={mToggleDatosPersonales}>
		<h4>{titleDatosPersonales}</h4>
	</ModalHeader>
	<ModalBody>
		<form
			id="frmDatosPersonales"
			on:submit|preventDefault={() => saveDatosPersonales(dtpersona.id)}
			autocomplete="off"
		>
			<div class="card-body">
				<div class="row g-3">
					
					<div class="col-md-6">
						<label for="eNombres" class="form-label fw-bold">
						<span class="fs-bold text-danger">(*)</span> Nombres: </label>
						<input
							type="text"
							class="form-control"
							id="eNombres"
							name="eNombres"
							bind:value={dtpersona.nombres}
						/>
					</div>	
					<div class="col-md-6">
						<label for="eApellido1" class="form-label fw-bold"> 
						<span class="fs-bold text-danger">(*)</span> 1er Apellido: </label>
						<input
							type="text"
							class="form-control"
							id="eApellido1"
							name="eApellido1"
							bind:value={dtpersona.apellido1}
						/>
					</div>	
					<div class="col-md-6">
						<label for="eApellido2" class="form-label fw-bold">
						<span class="fs-bold text-danger">(*)</span> 2do Apellido: </label>
						<input
							type="text"
							class="form-control"
							id="eApellido2"
							name="eApellido2"
							bind:value={dtpersona.apellido2}
						/>
					</div>	
					<div class="col-md-6">
						<label for="eCedula" class="form-label fw-bold">
						<span class="fs-bold text-danger">(*)</span> Cédula: </label>
						<input
							type="text"
							class="form-control"
							id="eCedula"
							name="eCedula"
							bind:value={dtpersona.cedula}
							disabled
							readonly
						/>
					</div>						
					<div class="col-md-6">
						<label for="ePasaporte" class="form-label fw-bold"> Pasaporte: </label>
						<input
							type="text"
							class="form-control"
							id="ePasaporte"
							name="ePasaporte"
							bind:value={dtpersona.pasaporte}
						/>
					</div>	
					<div class="col-md-6">
						<label for="eSexo" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Sexo:</label
						>
						<select class="form-control form-select" id="eSexo" bind:value={sexo}>
							{#each [{ value: 0, text: 'NINGUNO' }, { value: 1, text: 'MUJER' }, { value: 2, text: 'HOMBRE' }] as sexo}
								<option value={sexo.value}>
									{sexo.text}
								</option>
							{/each}
						</select>
					</div>					
					<div class="col-md-6">
						<label for="eEstadoCivil" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Estado civil: </label
						>
						<select class="form-control form-select" id="eEstadoCivil" bind:value={estadocivil_id}>
							<option value="" selected> ---------- </option>
							{#each estado_civil as civil }
								<option value={civil.idm}>
									{civil.nombre}
								</option>
							{/each}
						</select>
					</div>					
					<div class="col-md-6">
						<label for="eFechaNacimiento" class="form-label fw-bold">
						<span class="fs-bold text-danger">(*)</span> Fecha nacimiento: </label>
						<input
							type="date"
							class="form-control"
							id="eFechaNacimiento"
							name="eFechaNacimiento"
							bind:value={dtpersona.nacimiento}
						/>
					</div>					
					<div class="col-md-6">
						<label for="eAniosResidencia" class="form-label fw-bold"> Años de residencia: </label>
						<input
							type="text"
							class="form-control"
							id="eAniosResidencia"
							name="eAniosResidencia"
							bind:value={dtpersona.anioresidencia}
						/>
					</div>	
					<div class="col-md-6">
						<label for="eCorreoPersonal" class="form-label fw-bold">
						<span class="fs-bold text-danger">(*)</span> Correo electrónico personal: </label>
						<input
							type="text"
							class="form-control"
							id="eCorreoPersonal"
							name="eCorreoPersonal"
							bind:value={dtpersona.email}
						/>
					</div>	
					<div class="col-md-6">
						<label for="eCorreoInstitucional" class="form-label fw-bold">
						<span class="fs-bold text-danger">(*)</span> Correo electrónico Institucional: </label>
						<input
							type="text"
							class="form-control"
							id="eCorreoInstitucional"
							name="eCorreoInstitucional"
							bind:value={dtpersona.emailinst}
						/>
					</div>
					<div class="col-md-6">
						<label for="eLgbti" class="form-label fw-bold"> Grupo LGTBI:
						</label>
						<div class="form-check form-switch ">
							<input
								class="form-control form-check-input"
								type="checkbox"
								id="eLgbti"
								name="eLgbti"
								bind:checked={lgtbi}
							/>
							<label class="form-check-label fs-bold" for="eLgbti1"
								>¿Pertenece al Grupo LGTBI?</label
							>
						</div>
					</div>						
				</div>
				<div class="card-footer text-muted">
					<div class="d-grid gap-2 d-md-flex justify-content-md-end">
						<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
						<button type="submit" class="btn btn-success">Guardar</button>
						<a color="danger" class="btn btn-danger" on:click={() => closeDatosPersonalesForm()}
							>Cerrar</a
						>
					</div>
				</div>
			</div>
		</form>
	</ModalBody>
</Modal>

<Modal
	isOpen={mOpenDatosNacimiento}
	toggle={mToggleDatosNacimiento}
	size={mSizeDatosNacimiento}
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
	backdrop="static"
	fade={false}
>
	<ModalHeader toggle={mToggleDatosNacimiento}>
		<h4>{titleDatosNacimiento}</h4>
	</ModalHeader>
	<ModalBody>
		<form
			id="frmDatosNacimiento"
			on:submit|preventDefault={() => saveDatosNacimiento(dnpersona.id)}
			autocomplete="off"
		>
			<div class="card-body">
				<div class="row g-3">

					<div class="col-md-6">
						<label for="ePaisNacimiento" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Pais Nacimiento:</label
						>
						<Select id="ePaisNacimiento" placeholder="Pais..." 
							bind:value={selected_pais_nacimiento}
							on:select={changepaisnacimiento}																		
							items={pais_nacimiento}></Select>												
					</div>					
					<div class="col-md-6">
						<label for="eProvinciaNacimiento" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Provincia Nacimiento:</label
						>
						<Select id="eProvinciaNacimiento" placeholder="Provincia..." 
							bind:value={selected_provincia_nacimiento} 
							on:select={changeprovincianacimiento}	
							items={provincia_nacimiento}></Select>												
					</div>
					<div class="col-md-6">
						<label for="eCantonNacimiento" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Cantón Nacimiento:</label
						>
						<Select id="eCantonNacimiento" placeholder="Cantón..." 
							bind:value={selected_canton_nacimiento} 
							on:select={changecantonnacimiento}	
							items={canton_nacimiento}></Select>												
					</div>
					<div class="col-md-6">
						<label for="eParroquiaNacimiento" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Parroquia Nacimiento:</label
						>
						<Select id="eParroquiaNacimiento" placeholder="Parroquia..." 
							bind:value={selected_parroquia_nacimiento} 
							items={parroquia_nacimiento}></Select>												
					</div>				
					<div class="col-md-6">
						<label for="eNacionalidad" class="form-label fw-bold">
						<span class="fs-bold text-danger">(*)</span> Nacionalidad: </label>
						<input
							type="text"
							class="form-control"
							id="eNacionalidad"
							name="eNacionalidad"
							bind:value={nacionalidad}
						/>
					</div>					
					
				<div class="card-footer text-muted">
					<div class="d-grid gap-2 d-md-flex justify-content-md-end">
						<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
						<button type="submit" class="btn btn-success">Guardar</button>
						<a color="danger" class="btn btn-danger" on:click={() => closeDatosNacimientoForm()}
							>Cerrar</a
						>
					</div>
				</div>
			</div>
		</form>
	</ModalBody>
</Modal>

<Modal
	isOpen={mOpenDatosResidencia}
	toggle={mToggleDatosResidencia}
	size={mSizeDatosResidencia}
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
	backdrop="static"
	fade={false}
>
	<ModalHeader toggle={mToggleDatosResidencia}>
		<h4>{titleDatosResidencia}</h4>
	</ModalHeader>
	<ModalBody>
		<form
			id="frmDatosResidencia"
			on:submit|preventDefault={() => saveDatosResidencia(ddpersona.id)}
			autocomplete="off"
		>
			<div class="card-body">
				<div class="row g-3">
					<div class="col-md-6">
						<label for="ePaisResidencia" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Pais Domicilio:</label
						>
						<Select id="ePaisResidencia" placeholder="Pais..." 
							bind:value={selected_pais_residencia}
							on:select={changepaisdomicilio}																		
							items={pais_residencia}></Select>												
					</div>					
					<div class="col-md-6">
						<label for="eProvinciaResidencia" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Provincia Domicilio:</label
						>
						<Select id="eProvinciaResidencia" placeholder="Provincia..." 
							bind:value={selected_provincia_residencia} 
							on:select={changeprovinciadomicilio}	
							items={provincia_residencia}></Select>												
					</div>
					<div class="col-md-6">
						<label for="eCantonResidencia" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Cantón Domicilio:</label
						>
						<Select id="eCantonResidencia" placeholder="Cantón..." 
							bind:value={selected_canton_residencia} 
							on:select={changecantondomicilio}	
							items={canton_residencia}></Select>												
					</div>
					<div class="col-md-6">
						<label for="eParroquiaResidencia" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Parroquia Domicilio:</label
						>
						<Select id="eParroquiaResidencia" placeholder="Parroquia..." 
							bind:value={selected_parroquia_residencia} 
							items={parroquia_residencia}></Select>												
					</div>																						
					<div class="col-md-6">
						<label for="eCallePrincipal" class="form-label fw-bold">
						<span class="fs-bold text-danger">(*)</span> Calle Principal: </label>
						<input
							type="text"
							class="form-control"
							id="eCallePrincipal"
							name="eCallePrincipal"
							bind:value={direccion_residencia}
						/>
					</div>	
					<div class="col-md-6">
						<label for="eCalleSecundaria" class="form-label fw-bold">
						 Calle Secundaria: </label>
						<input
							type="text"
							class="form-control"
							id="eCalleSecundaria"
							name="eCalleSecundaria"
							bind:value={direccion2_residencia}
						/>
					</div>		
					<div class="col-md-6">
						<label for="eNumeroResidencia" class="form-label fw-bold">
						Número(Domicilio): </label>
						<input
							type="text"
							class="form-control"
							id="eNumeroResidencia"
							name="eNumeroResidencia"
							bind:value={num_direccion_residencia}
						/>
					</div>		
					<div class="col-md-6">
						<label for="eReferencia" class="form-label fw-bold">
						Referencia: </label>
						<input
							type="text"
							class="form-control"
							id="eReferencia"
							name="eReferencia"
							bind:value={referencia_residencia}
						/>
					</div>		
					<div class="col-md-6">
						<label for="eTelefonoDomicilio" class="form-label fw-bold">
						 Teléfono domicilio: </label>
						<input
							type="text"
							class="form-control"
							id="eTelefonoDomicilio"
							name="eTelefonoDomicilio"
							bind:value={telefono_conv_residencia}
						/>
					</div>		
					<div class="col-md-6">
						<label for="eCelular" class="form-label fw-bold">
						<span class="fs-bold text-danger">(*)</span> Celular: </label>
						<input
							type="text"
							class="form-control"
							id="eCelular"
							name="eCelular"
							bind:value={telefono_residencia}
						/>
					</div>						
					
				<div class="card-footer text-muted">
					<div class="d-grid gap-2 d-md-flex justify-content-md-end">
						<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
						<button type="submit" class="btn btn-success">Guardar</button>
						<a color="danger" class="btn btn-danger" on:click={() => closeDatosResidenciaForm()}
							>Cerrar</a
						>
					</div>
				</div>
			</div>
		</form>
	</ModalBody>
</Modal>

<Modal
	isOpen={mOpenDatosEtnia}
	toggle={mToggleDatosEtnia}
	size={mSizeDatosEtnia}
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
	backdrop="static"
	fade={false}
>
	<ModalHeader toggle={mToggleDatosEtnia}>
		<h4>{titleDatosEtnia}</h4>
	</ModalHeader>
	<ModalBody>
		<form
			id="frmDatosEtnia"
			on:submit|preventDefault={() => saveDatosEtnia(perfilinscripcion.id)}
			autocomplete="off"
		>
			<div class="card-body">
				<div class="row g-3">	
					
					<div class="col-md-6">
						<label for="eRaza" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Seleccione Etnia:</label
						>
						<Select id="eRaza" placeholder="Etnia..." 
							bind:value={selected_raza}																									
							items={razas}></Select>												
					</div>
					<div class="col-md-6">
						<label for="eNacionalidadIndigena" class="form-label fw-bold"
							> Seleccione Nacionalidad Indígena:</label
						>
						<Select id="eNacionalidadIndigena" placeholder="Nacionalidad Indígena..." 
							bind:value={selected_nacionalidadindigena}																									
							items={nacionalidadesindigena}></Select>												
					</div>																							
					
				<div class="card-footer text-muted">
					<div class="d-grid gap-2 d-md-flex justify-content-md-end">
						<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
						<button type="submit" class="btn btn-success">Guardar</button>
						<a color="danger" class="btn btn-danger" on:click={() => closeDatosEtniaForm()}
							>Cerrar</a
						>
					</div>
				</div>
			</div>
		</form>
	</ModalBody>
</Modal>

<Modal
	isOpen={mOpenDatosTitulacion}
	toggle={mToggleDatosTitulacion}
	size={mSizeDatosTitulacion}
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
	backdrop="static"
	fade={false}
>
	<ModalHeader toggle={mToggleDatosTitulacion}>
		<h4>{titleDatosTitulacion}</h4>
	</ModalHeader>
	<ModalBody>
		<form
			id="frmDatosTitulacion"
			on:submit|preventDefault={() => saveDatosTitulacion(titulacion_id)}
			autocomplete="off"
		>
			<div class="card-body">
				<div class="row g-3">																							

					<div class="col-md-12">
						<label for="eTitulo" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Seleccione Título:</label
						>

						<FormSelectSearch
								inputId="eTitulo"
								name="eTitulo"
								bind:value={selected_titulo}
								on:actionChangeSelectSearch={changeTitulo}
								fetch={(query) => getTitulos(query,3)}
							/>
					</div>				
										
					<div class="col-md-12">
						<label for="eInstitucionEdu" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Seleccione Institución Educativa:</label
						>
						<Select id="eInstitucionEdu" placeholder="Institución Educativa..." bind:value={selected_institucion} items={instituciones}></Select>
												
					</div>

					<div class="col-md-6">
						<label for="eNumRegistro" class="form-label fw-bold">
						<span class="fs-bold text-danger">(*)</span> N° Registro SENESCYT: </label>
						<input
							type="text"
							class="form-control"
							id="eNumRegistro"
							name="eNumRegistro"
							bind:value={tituloregistro}
						/>
					</div>
					<div class="col-md-12">
						<label for="eTituloFileDocumento" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Documento del Título:</label
						>
						<FilePond
							id="eTituloFileDocumento"
							class="pb-0 mb-0"
							bind:this={pondTitulo}
							{nameTitulo}
							labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
							allowMultiple={true}
							oninit={handleInit}
							onaddfile={handleAddFile}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxParallelUploads="1"
						/>
						{#if tituloArchivo != ''}
							<a
								title="VER TÍTULO"
								href="{variables.BASE_API}{tituloArchivo}"
								target="_blank">{tituloArchivo}</a
							><br />
						{/if}
						<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
					</div>		
					<div class="col-md-12">
						<label for="eSenescytFileDocumento" class="form-label fw-bold"
							>Documento de SENESCYT:</label
						>
						<FilePond
							id="eSenescytFileDocumento"
							class="pb-0 mb-0"
							bind:this={pondSenescyt}
							{nameSenescyt}
							labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
							allowMultiple={true}
							oninit={handleInit}
							onaddfile={handleAddFile}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxParallelUploads="1"
						/>
						{#if tituloSenescyt != ''}
							<a
								title="VER DOCUMENTO SENESCYT"
								href="{variables.BASE_API}{tituloSenescyt}"
								target="_blank">{tituloSenescyt}</a
							><br />
						{/if}
						<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
					</div>	
					
				</div>	
				<div class="card-footer text-muted">
					<div class="d-grid gap-2 d-md-flex justify-content-md-end">
						<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
						<button type="submit" class="btn btn-success">Guardar</button>
						<a color="danger" class="btn btn-danger" on:click={() => closeDatosTitulacionForm()}
							>Cerrar</a
						>
					</div>
				</div>
			</div>
		</form>
	</ModalBody>
</Modal>

{#if mOpenModalGenerico}
	<ModalGenerico
		mToggle={mToggleModalGenerico}
		mOpen={mOpenModalGenerico}
		modalContent={modalDetalleContent}
		title={modalTitle}
		aData={aDataModal}
		size="xl"
	/>
{/if}
<style global>
	@import 'filepond/dist/filepond.css';
</style>
