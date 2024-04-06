<script lang="ts">
    export let aData;
    import type {Load} from '@sveltejs/kit';
    import {browserGet, apiPOST, apiPOSTFormData, apiGET} from '$lib/utils/requestUtils';
    import {variables} from '$lib/utils/constants';
    import Swal from 'sweetalert2';
    import {addToast} from '$lib/store/toastStore';
    import {addNotification} from '$lib/store/notificationStore';
    import {loading} from '$lib/store/loadingStore';
    import {Badge, Button, Form, FormGroup, FormText, Input, Label} from 'sveltestrap';
    import {createEventDispatcher, onDestroy} from 'svelte';
    import {onMount} from 'svelte';
    import {goto} from '$app/navigation';

    let errors: { [inputName: string]: any } = {};

    function isFormValid(data: { [inputName: string]: any }): boolean {
        return !Object.keys(errors).some((inputName) =>
            Object.keys(errors[inputName]).some((errorName) => errors[inputName][errorName])
        );
    }

    function validateForm(data: { [inputName: string]: any }): void {
        console.log(data)
        if (!isRequiredFieldValid(data.borrador_articulo.name)) {
            errors['borrador_articulo'] = {...errors['borrador_articulo'], required: true};
        } else {
            errors['borrador_articulo'] = {...errors['borrador_articulo'], required: false};
        }

        if (!isRequiredFieldValid(data.carta_de_aceptacion.name)) {
            errors['carta_de_aceptacion'] = {...errors['carta_de_aceptacion'], required: true};
        } else {
            errors['carta_de_aceptacion'] = {...errors['carta_de_aceptacion'], required: false};
        }

        if (!isRequiredFieldValid(data.acta_de_acompanamieno.name)) {
            errors['acta_de_acompanamieno'] = {...errors['acta_de_acompanamieno'], required: true};
        } else {
            errors['acta_de_acompanamieno'] = {...errors['acta_de_acompanamieno'], required: false};
        }
          if (!isRequiredFieldValid('linkrevista')) {
            errors['linkrevista'] = {...errors['linkrevista'], required: true};
        } else {
            errors['linkrevista'] = {...errors['linkrevista'], required: false};
        }


    }

    function isRequiredFieldValid(value) {
        return value != null && value !== '';
    }

    const dispatch = createEventDispatcher();

    const save = async (formData) => {
        loading.setLoading(true, 'Guardando la información, espere por favor...');
        formData.append('action', 'adddocumentofinaltitulacionpormecanismo');
        formData.append('id', aData.grupo.id);
        formData.append('id_tutoria', aData.id_tutoria);
        formData.append('es_pareja', aData.es_pareja);
        const [res, errors] = await apiPOSTFormData(fetch, 'alumno/tematitulacion_posgrado', formData);
        if (errors.length > 0) {
            addToast({type: 'error', header: 'Ocurrio un error', body: errors[0].error});
            loading.setLoading(false, 'Cargando, espere por favor...');
            return;
        } else {
            if (!res.isSuccess) {
                addToast({type: 'error', header: 'Ocurrio un error', body: res.message});
                if (!res.module_access) {
                    goto('/');
                }
                loading.setLoading(false, 'Cargando, espere por favor...');
                return;
            } else {
                addToast({type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos'});
                loading.setLoading(false, 'Cargando, espere por favor...');
                dispatch('actionRun', {action: 'nextProccess', value: 1});
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
        validateForm(data);
        if (isFormValid(data)) {
            save(formData);
        } else {
            addToast({
                type: 'error',
                header: 'Form invalid',
                body: 'Complete todos los campos correctamente.'
            });
        }
    }

    onMount(async () => {
    });
</script>

<form id="FormAddDocEnsayo" on:submit|preventDefault={onSubmit}>
    {#each aData.grupo.documentos_tutoria_configurado as documento}
        <div class="col-12 mb-4" id="{documento.fieldset}">
            <FormGroup>
                <Label class="mb-3" for="{documento.id_field}">{documento.display} :<span
                        class="text-danger">*</span></Label>
                <Input class="required" type="file" name="{documento.name_field}" id="{documento.id_field} "/>
            </FormGroup>

        </div>
    {/each}
    <div class="mb-3 col-12" id="fieldset_linkrevista">
        <Label class="form-label" > LINK DE LA REVISTA <span class="text-danger">*</span></Label>
        <input class="form-control " required name="linkrevista"	id="id_linkrevista" placeholder="Ingrese Link de la revista" />

    </div>
    <div class="row">
        <div class="col-md-8"/>
        <div class="col-12 mb-4">
            <button type="submit" class="btn btn-success form-control">Guardar</button>
        </div>
    </div>
</form>
