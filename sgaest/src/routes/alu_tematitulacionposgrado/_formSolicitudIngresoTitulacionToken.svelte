<script lang="ts">
	import Select from "svelte-select";

	export let aData;
	import type { Load } from '@sveltejs/kit';
	import { browserGet, apiPOST, apiPOSTFormData, apiGET } from '$lib/utils/requestUtils';
	import { variables } from '$lib/utils/constants';
	import Swal from 'sweetalert2';
	import { addToast } from '$lib/store/toastStore';
	import { addNotification } from '$lib/store/notificationStore';
	import { loading } from '$lib/store/loadingStore';
	import { Badge, Button, Form, FormGroup, FormText, Input, Label } from 'sveltestrap';
	import { createEventDispatcher, onDestroy } from 'svelte';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let errors: { [inputName: string]: any } = {};
	let mecanismos = [];
	let selected_mecanismo=0;



	function isRequiredFieldValid(value) {
		return value != null && value !== '';
	}
	const dispatch = createEventDispatcher();




	const descargar_pdf_solicitud_ingreso_titulacion = async (formData) =>{
		const [res, errors] =await apiPOSTFormData(fetch, 'alumno/tematitulacion_posgrado', formData);
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

				let a = "https://sga.unemi.edu.ec"
				window.open(a+res.data.file_url, '_blank');

			}
		}
	};


	const save = async (formData) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		descargar_pdf_solicitud_ingreso_titulacion(formData)

		loading.setLoading(false, 'Cargando, espere por favor...');
		dispatch('actionRun', { action: 'nextProccess', value: 1 });
		addToast({ type: 'success', header: 'Exitoso', body: 'Se genero correctamente el documento' });
	};

	function onSubmit(e) {
		const formData = new FormData(e.target);
		formData.append('action', 'descargar_pdf_solicitud_ingreso_titulacion');
		formData.append('mecanismo_id', selected_mecanismo.obtenerid);
		console.log(formData)
		debugger;
		const data: any = {};
		for (let field of formData) {
			const [key, value] = field;
			data[key] = value;
		}
		save(formData);
	}

	onMount(async () => {
		mecanismos = aData.formImputMecanismoTitulacion;
	});
</script>

<form id="FormCorreccionTribunal" on:submit|preventDefault={onSubmit}>
	<div class="row">
		<!-- form group -->
		<div class="mb-3 col-12">
			<label class="form-label" >
				Mecánismo Titulación <span class="text-danger">*</span></label
			>

			<Select placeholder="-----------"  bind:value={selected_mecanismo} id="id_mecanismotitulacionposgrado" required name="mecanismotitulacionposgrado" items={mecanismos} label="display"  itemId='id'></Select>
		</div>
		<div class="row" style="margin-left: -1px;!important;">

		</div>
		<br>



		<div class="col-md-8" />
		<div class="col-12 mb-4">
			<button type="submit" class="btn btn-success form-control">Generar archivo de solicitud</button>
		</div>
	</div>
</form>
