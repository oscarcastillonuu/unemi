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

	const save = async (formData) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');

		debugger;

		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/tematitulacion_posgrado', formData);
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				loading.setLoading(false, 'Cargando, espere por favor...');
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
			}
		}
	};

	function onSubmit(e) {
		const formData = new FormData(e.target);
		formData.append('action', 'firmar_solicitud_ingreso_titulacion');
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

			<Select  placeholder="-----------"  bind:value={selected_mecanismo} id="id_mecanismotitulacionposgrado" required name="mecanismotitulacionposgrado" items={mecanismos} label="display"  itemId='id'></Select>
		</div>
		<div class="row" style="margin-left: -1px;!important;">
			<textarea style="display: none;" name="txtFirmas"></textarea>
			<div id="fieldset_firma" class="col-sm-12" style="float: left;width: 100%">
				<label class="control-label pr-2" for="id_firma"><b>Firma Electrónica<span
						style="color:red;margin-left:2px;"><strong>*</strong></span>&nbsp;:</b></label>
				<input type="file" name="firma" class="form-control" required id="id_firma" accept=".p12,.pfx"
					   style="padding: 12px 6px !important;width:100%;">
				<p class="help-text">Formato permitido .p12 y .pfx </p>
			</div>
			<div id="fieldset_pass" class="col-sm-12" style="float: left; padding-right: 10px;">
				<label class="control-label pr-2" ><b>Contraseña<span
						style="color:red;margin-left:2px;"><strong>*</strong></span>&nbsp;:</b></label>
				<input type="password" name="palabraclave" class="form-control" required id="id_palabraclave"
					   placeholder="Contraseña">
			</div>
			<small style="text-align: justify;" class="text-danger"><b>Nota:</b> Para proteger a nuestros usuarios le
				recordamos que ninguna firma usada en nuestras plataformas quedará guardada.</small>
		</div>
		<br>



		<div class="col-md-8" />
		<div class="col-12 mb-4">
			<button type="submit" class="btn btn-success form-control">Firmar y Guardar</button>
		</div>
	</div>
</form>
