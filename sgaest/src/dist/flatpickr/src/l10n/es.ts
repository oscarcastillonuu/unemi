/* Spanish locals for flatpickr */
import type { CustomLocale } from "$dist/flatpickr/src/types/locale";
import type { FlatpickrFn } from "$dist/flatpickr/src/types/instance";

const fp =
  typeof window !== "undefined" && window.flatpickr !== undefined
    ? window.flatpickr
    : ({
        l10ns: {},
      } as FlatpickrFn);

export const Spanish: CustomLocale = {
  weekdays: {
    shorthand: ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"],
    longhand: [
      "Domingo",
      "Lunes",
      "Martes",
      "Miércoles",
      "Jueves",
      "Viernes",
      "Sábado",
    ],
  },

  months: {
    shorthand: [
      "Ene",
      "Feb",
      "Mar",
      "Abr",
      "May",
      "Jun",
      "Jul",
      "Ago",
      "Sep",
      "Oct",
      "Nov",
      "Dic",
    ],
    longhand: [
      "Enero",
      "Febrero",
      "Marzo",
      "Abril",
      "Mayo",
      "Junio",
      "Julio",
      "Agosto",
      "Septiembre",
      "Octubre",
      "Noviembre",
      "Diciembre",
    ],
  },

  ordinal: () => {
    return "º";
  },

  firstDayOfWeek: 1,
  rangeSeparator: " a ",
  time_24hr: true,
};

fp.l10ns.es = Spanish;

export default fp.l10ns;