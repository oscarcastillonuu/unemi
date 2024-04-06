<script lang="ts">
    import {Label} from "sveltestrap";
    import Select from "svelte-select";
    import {createEventDispatcher, onMount} from "svelte";
    import {addToast} from "$lib/store/toastStore";
    import {loading} from "$lib/store/loadingStore";
    import {apiPOSTFormData} from "$lib/utils/requestUtils";
    import {goto} from "$app/navigation";
    export let aData;


    let tipoarchivos = [
        {value: 'certificado_medico', label: `Certificado médico`},
        {value: 'certificado_upc', label: `Certificado UPC`},
        {value: 'certificado_defuncion', label: `Certificado de defunción`},
        {value: 'certificado_licencia', label: `Certificado de licencia`},
        {value: 'certificado_alterno', label: `Certificado alterno`}
    ];
    let selected_tipoarchivos;

    function visualizar_fieldset(field_set = null, visible = false) {
        if (visible === false) {
            field_set.style.display = 'none';
        } else {
            field_set.style.display = 'block';
        }

    }
    const dispatch = createEventDispatcher();



    function changeTipoArchivo() {
        let tipo = selected_tipoarchivos['value']

        if (tipo === 'certificado_medico') {
            visualizar_fieldset(document.getElementById('fieldset_certificado_medico'), true);
            visualizar_fieldset(document.getElementById('fieldset_certificado_upc'), false);
            visualizar_fieldset(document.getElementById('fieldset_certificado_defuncion'), false);
            visualizar_fieldset(document.getElementById('fieldset_certificado_licencia'), false);
            visualizar_fieldset(document.getElementById('fieldset_certificado_alterno'), false);
        } else if (tipo === 'certificado_upc') {
            visualizar_fieldset(document.getElementById('fieldset_certificado_medico'), false);
            visualizar_fieldset(document.getElementById('fieldset_certificado_upc'), true);
            visualizar_fieldset(document.getElementById('fieldset_certificado_defuncion'), false);
            visualizar_fieldset(document.getElementById('fieldset_certificado_licencia'), false);
            visualizar_fieldset(document.getElementById('fieldset_certificado_alterno'), false);
        } else if (tipo === 'certificado_defuncion') {
            visualizar_fieldset(document.getElementById('fieldset_certificado_medico'), false);
            visualizar_fieldset(document.getElementById('fieldset_certificado_upc'), false);
            visualizar_fieldset(document.getElementById('fieldset_certificado_defuncion'), true);
            visualizar_fieldset(document.getElementById('fieldset_certificado_licencia'), false);
            visualizar_fieldset(document.getElementById('fieldset_certificado_alterno'), false);
        } else if (tipo === 'certificado_licencia') {
            visualizar_fieldset(document.getElementById('fieldset_certificado_medico'), false);
            visualizar_fieldset(document.getElementById('fieldset_certificado_upc'), false);
            visualizar_fieldset(document.getElementById('fieldset_certificado_defuncion'), false);
            visualizar_fieldset(document.getElementById('fieldset_certificado_licencia'), true);
            visualizar_fieldset(document.getElementById('fieldset_certificado_alterno'), false);
        } else if (tipo === 'certificado_alterno') {
            visualizar_fieldset(document.getElementById('fieldset_certificado_medico'), false);
            visualizar_fieldset(document.getElementById('fieldset_certificado_upc'), false);
            visualizar_fieldset(document.getElementById('fieldset_certificado_defuncion'), false);
            visualizar_fieldset(document.getElementById('fieldset_certificado_licencia'), false);
            visualizar_fieldset(document.getElementById('fieldset_certificado_alterno'), true);
        }
    }

    onMount(() => {
        visualizar_fieldset(document.getElementById('fieldset_certificado_medico'), false);
        visualizar_fieldset(document.getElementById('fieldset_certificado_upc'), false);
        visualizar_fieldset(document.getElementById('fieldset_certificado_defuncion'), false);
        visualizar_fieldset(document.getElementById('fieldset_certificado_licencia'), false);
        visualizar_fieldset(document.getElementById('fieldset_certificado_alterno'), false);
    });


    const save = async (formData) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		formData.append('action', 'add');
		formData.append('id', aData.id);
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/procesoelectoral/justificativo', formData);
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

		const data: any = {};
		for (let field of formData) {
			const [key, value] = field;
			data[key] = value;
		}
        save(formData);

	}


</script>

<form id="FormJustificacion" on:submit|preventDefault={onSubmit}>
<div class="alert alert-info" role="alert" style="text-align: justify; font-size: 12px">
    <b class="alert-heading"><i class="fe fe-help-circle"></i> Atención</b> Se debe subir un solo documento en base a la
    categoría a la que se acoja para justificar la omisión del
    sufragio. Este debe de estar escaneado de forma legible, pues no se aceptará documentación que se suba en mal estado
    o con falta de visibilidad.
    Todo esto hasta el . En lo posterior, el TEI validará su solicitud en el término de 8 días contados desde la fecha
    posterior a la elección.
</div>


<div id="fieldset_tipoarchivo" class="col-lg-12 ">
    <Label class="form-label" for="id_tipoarchivo">Observación <span class="text-danger">*</span></Label>
    <Select placeholder="Seleccionar una opción" bind:value={selected_tipoarchivos} id="id_tipoarchivo"
            on:change={changeTipoArchivo}
            name="tipoarchivo" items={tipoarchivos}></Select>
</div>
<div id="fieldset_certificado_medico" class="form-group">
    <label for="id_certificado_medico" class="control-label pr-2"><span class="fs-bold text-danger">(*)</span>
        Impedimento físico o enfermedad&nbsp;:</label>
    <input type="file" name="certificado_medico" class="form-control" id="id_certificado_medico">
    <small class="text-warning">Subir Certificado médico de centro de salud publica o IESS, Tamaño maximo 4mb en formato
        pdf, jpg, jpeg</small>
</div>

<div id="fieldset_certificado_upc" class="form-group">
    <label for="id_certificado_upc" class="control-label pr-2"><span class="fs-bold text-danger">(*)</span> Fué detenido
        el día de las elecciones&nbsp;:</label>
    <input type="file" name="certificado_upc" class="form-control" id="id_certificado_upc">
    <small class="text-warning">Subir Certificado de UPC de haber sido detenido, Tamaño maximo 4mb en formato pdf, jpg,
        jpeg</small>
</div>

<div id="fieldset_certificado_defuncion" class="form-group">
    <label for="id_certificado_defuncion" class="control-label pr-2"><span class="fs-bold text-danger">(*)</span>
        Fallecio un familiar hasta de 4to grado de consanguinidad&nbsp;:</label>
    <input type="file" name="certificado_defuncion" class="form-control" id="id_certificado_defuncion">
    <small class="text-warning">Subir Certificado de defunción, Tamaño maximo 4mb en formato pdf, jpg, jpeg</small>
</div>

<div id="fieldset_certificado_licencia" class="form-group">
    <label for="id_certificado_licencia" class="control-label pr-2"><span class="fs-bold text-danger">(*)</span> Cuenta
        con licencia y no pudo presentarse al sufragio&nbsp;:</label>
    <input type="file" name="certificado_licencia" class="form-control" id="id_certificado_licencia">
    <small class="text-warning">Subir Certificado de licencia, Tamaño maximo 4mb en formato pdf, jpg, jpeg </small>
</div>

<div id="fieldset_certificado_alterno" class="form-group">
    <label for="id_certificado_alterno" class="control-label pr-2"><span class="fs-bold text-danger">(*)</span> Cuenta
        con un justificativo distinto a las causales anteriores&nbsp;:</label>
    <input type="file" name="certificado_alterno" class="form-control" id="id_certificado_alterno">
    <small class="text-warning">Subir Certificado Alterno, Tamaño maximo 4mb en formato pdf, jpg, jpeg</small>
</div>

<div id="fieldset_observacion" class="col-lg-12 ">
    <label class="control-label pr-2" for="id_observacion"><b>Observación<span
            style="color:red;margin-left:2px;"><strong>*</strong></span>&nbsp;:</b></label>
    <textarea name="observacion" cols="40" rows="6" maxlength="900" placeholder="Máximo 150 palabras"
              class="form-control" col="12" data-nameinput="observacion" required="" id="id_observacion"></textarea>
    <small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
</div>

<div class="col-md-8"/>
<div class="col-12 mb-4">
    <button type="submit" class="btn btn-success form-control">Guardar</button>
</div>

</form>
