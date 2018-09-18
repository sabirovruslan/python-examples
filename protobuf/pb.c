#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "deviceapps.pb-c.h"

#define MAGIC  0xFFFFFFFF
#define DEVICE_APPS_TYPE 1

typedef struct pbheader_s {
    uint32_t magic;
    uint16_t type;
    uint16_t length;
} pbheader_t;

#define PBHEADER_INIT {MAGIC, 0, 0}

static PyObject* bufiter_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    char *filename;
    PyObject *gz_file;

    if ( !PyArg_ParseTuple(args, "s", &filename) ) {
        return NULL;
    } else {
        gz_file = PyCapsule_New((void*) gzopen(filename, "r6h"), NULL, NULL);
    }

    BufIterState *bistate = (BufIterState *) type->tp_alloc(type, 0);
    if ( !bistate ) {
        gzclose((gzFile) PyCapsule_GetPointer(gz_file, NULL));
        return NULL;
    }

    bistate->gz_file = gz_file;

    return (PyObject *)bistate;
}

static void bufiter_dealloc(BufIterState *bistate) {
    gzclose((gzFile) PyCapsule_GetPointer(bistate->gz_file, NULL));
}

static PyObject* parse_device(char *buf, int length) {
     DeviceApps *msg = device_apps__unpack (NULL, length, (const uint8_t*) buf);
     DeviceApps__Device *device = msg->device;
     PyObject *item = PyDict_New();
     PyObject *dev = PyDict_New();

     if ( device->has_id ) {
         PyObject *id = PyString_FromStringAndSize((char *) device->id.data, device->id.len);
         PyDict_SetItemString(dev, "id", id);
     }

     if ( device->has_type ) {
         PyObject *type = PyString_FromStringAndSize((char *) device->type.data, device->type.len);
         PyDict_SetItemString(dev, "type", type);
     }

     PyDict_SetItemString(item, "device", dev);

     if ( msg->has_lat ) {
         PyObject *lat = PyFloat_FromDouble(msg->lat);
         PyDict_SetItemString(item, "lat", lat);
     }

     if ( msg->has_lon ) {
         PyObject *lon = PyFloat_FromDouble(msg->lon);
         PyDict_SetItemString(item, "lon", lon);
     }

     PyObject *apps;
     apps = PyList_New(0);

     for (size_t i = 0; i < msg->n_apps; ++i) {
         PyObject *app = PyInt_FromLong(msg->apps[i]);
         PyList_Append(apps, app);
     }

     PyDict_SetItemString(item, "apps", apps);
     return item;
}

static PyObject* bufiter_next(BufIterState *bistate)
{
    gzFile gz_file = (gzFile) PyCapsule_GetPointer(bistate->gz_file, NULL);
    pbheader_t next_header;
    int ret;

    /* Stop iteration if we can't read new header */
    if ( 0 == (ret = gzread(gz_file, &next_header, 8)) )
        return NULL;

    char *buf = (char *) malloc(next_header.length);

    if( gzread(gz_file, (void *) buf, next_header.length) != next_header.length ) {
        PyErr_SetString(PyExc_ValueError, "Bad string in the file");
        return NULL;
    } else if ( next_header.type != DEVICE_APPS_TYPE )   // Iterate only over DEVICE_APPS_TYPE
        return bufiter_next(bistate);

    PyObject *pobj_device = parse_device(buf, next_header.length);
    free(buf);
    return pobj_device;
}

PyTypeObject BufIter_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "bufiter",                      /* tp_name */
    sizeof(BufIterState),           /* tp_basicsize */
    0,                              /* tp_itemsize */
    (destructor)bufiter_dealloc,    /* tp_dealloc */
    0,                              /* tp_print */
    0,                              /* tp_getattr */
    0,                              /* tp_setattr */
    0,                              /* tp_reserved */
    0,                              /* tp_repr */
    0,                              /* tp_as_number */
    0,                              /* tp_as_sequence */
    0,                              /* tp_as_mapping */
    0,                              /* tp_hash */
    0,                              /* tp_call */
    0,                              /* tp_str */
    0,                              /* tp_getattro */
    0,                              /* tp_setattro */
    0,                              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,
                                    /* tp_flags */
    "Buffer iterator",              /* tp_doc */
    0,                              /* tp_traverse */
    0,                              /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    PyObject_SelfIter,              /* tp_iter */
    (iternextfunc)bufiter_next,     /* tp_iternext */
    0,                              /* tp_methods */
    0,                              /* tp_members */
    0,                              /* tp_getset */
    0,                              /* tp_base */
    0,                              /* tp_dict */
    0,                              /* tp_descr_get */
    0,                              /* tp_descr_set */
    0,                              /* tp_dictoffset */
    0,                              /* tp_init */
    PyType_GenericAlloc,            /* tp_alloc */
    bufiter_new,                    /* tp_new */
    0,                              /* tp_free */
    0,                              /* tp_is_gc */
    0,                              /* *tp_bases */
    0,                              /* *tp_mro */
    0,                              /* *tp_cache */
    0,                              /* *tp_subclasses */
    0,                              /* *tp_weaklist */
    0,                              /* tp_del */
    0,                              /* tp_version_tag */
};

size_t write_app(PyObject *app, gzFile gz_file) {
    DeviceApps msg = DEVICE_APPS__INIT;
    DeviceApps__Device device = DEVICE_APPS__DEVICE__INIT;

    pbheader_t header = PBHEADER_INIT;
    header.type = DEVICE_APPS_TYPE;

    void *buf;
    unsigned len, h_size;

    PyObject *pobj_device = PyDict_GetItemString(app, "device");
    if ( NULL == pobj_device ) {
        PyErr_SetString(PyExc_ValueError, "Dictionary should contain key device with value PyDictObject");
        return 0;
    }

    PyObject *pobj_device_id = PyDict_GetItemString(pobj_device, "id");
    if ( NULL == pobj_device_id ) {
        device.has_id = 0;
    } else {
        char *device_id = PyString_AsString(pobj_device_id);
        device.has_id = 1;
        device.id.data = (uint8_t*)device_id;
        device.id.len = strlen(device_id);
    }

    PyObject *pobj_device_type = PyDict_GetItemString(pobj_device, "type");
    if ( NULL == pobj_device_type ) {
        device.has_type = 0;
    } else {
        char *device_type = PyString_AsString(pobj_device_type);
        device.has_type = 1;
        device.type.data = (uint8_t*)device_type;
        device.type.len = strlen(device_type);
    }

    msg.device = &device;

    PyObject *pobj_lat = PyDict_GetItemString(app, "lat");
    if ( NULL == pobj_lat ) {
        msg.has_lat = 0;
    } else {
        msg.has_lat = 1;
        msg.lat = PyFloat_AsDouble(pobj_lat);
    }

    PyObject *pobj_lon = PyDict_GetItemString(app, "lon");
    if ( NULL == pobj_lon ) {
        msg.has_lon = 0;
    } else {
        msg.has_lon = 1;
        msg.lon = PyFloat_AsDouble(pobj_lon);
    }

    PyObject *pobj_apps = PyDict_GetItemString(app, "apps");
    if ( NULL == pobj_apps ) {
        PyErr_SetString(PyExc_ValueError, "Dictionary should contain key apps with value PyListObject");
        return 0;
    }

    msg.n_apps = PyList_Size(pobj_apps);
    msg.apps = malloc(sizeof(uint32_t) * msg.n_apps);

    for (size_t i = 0; i < msg.n_apps; ++i) {
        PyObject *pobj_app_num = PyList_GetItem(pobj_apps, i);
        msg.apps[i] = PyInt_AsLong(pobj_app_num);
    }

    /* Get length of strings to write to */
    len = device_apps__get_packed_size(&msg);
    h_size = sizeof(header);

    buf = malloc(len);
    device_apps__pack(&msg, buf);
    header.length = len;

    int ret = gzwrite(gz_file, (void *) &header, h_size);
    ret += gzwrite(gz_file, buf, len);

    free(msg.apps);
    free(buf);

    return ret;
}

// https://github.com/protobuf-c/protobuf-c/wiki/Examples
void example() {
    DeviceApps msg = DEVICE_APPS__INIT;
    DeviceApps__Device device = DEVICE_APPS__DEVICE__INIT;
    void *buf;
    unsigned len;

    char *device_id = "e7e1a50c0ec2747ca56cd9e1558c0d7c";
    char *device_type = "idfa";
    device.has_id = 1;
    device.id.data = (uint8_t*)device_id;
    device.id.len = strlen(device_id);
    device.has_type = 1;
    device.type.data = (uint8_t*)device_type;
    device.type.len = strlen(device_type);
    msg.device = &device;

    msg.has_lat = 1;
    msg.lat = 67.7835424444;
    msg.has_lon = 1;
    msg.lon = -22.8044005471;

    msg.n_apps = 3;
    msg.apps = malloc(sizeof(uint32_t) * msg.n_apps);
    msg.apps[0] = 42;
    msg.apps[1] = 43;
    msg.apps[2] = 44;
    len = device_apps__get_packed_size(&msg);

    buf = malloc(len);
    device_apps__pack(&msg, buf);

    fprintf(stderr,"Writing %d serialized bytes\n",len); // See the length of message
    fwrite(buf, len, 1, stdout); // Write to stdout to allow direct command line piping

    free(msg.apps);
    free(buf);
}

// Read iterator of Python dicts
// Pack them to DeviceApps protobuf and write to file with appropriate header
// Return number of written bytes as Python integer
static PyObject* py_deviceapps_xwrite_pb(PyObject* self, PyObject* args) {
    const char* path;
    PyObject* apps;
    long num_bytes = 0;

    if (!PyArg_ParseTuple(args, "Os", &apps, &path))
        return NULL;

    gzFile gz_file;
    if ( Z_NULL == (gz_file = gzopen(path, "w7h")) ) {
        PyErr_SetString(PyExc_IOError, "Cannot open file");
        return 0;
    }

    PyObject *iterator = PyObject_GetIter(apps);
    PyObject *app;

    /* Iterate through apps to write them down to the file */
    if ( NULL == iterator ) {
        PyErr_SetString(PyExc_ValueError, "Object is not iterable");
        return NULL;
    }

    while ( (app = PyIter_Next(iterator)) ) {
        num_bytes += write_app(app, gz_file);
        if ( PyErr_Occurred() ) {
            gzclose(gz_file);
            return NULL;
        }
        Py_DECREF(app);
    }

    Py_DECREF(iterator);

    printf("Write to %s %ld bytes\n", path, num_bytes);
    gzclose(gz_file);

    return PyInt_FromLong(num_bytes);
}

// Unpack only messages with type == DEVICE_APPS_TYPE
// Return iterator of Python dicts
static PyObject* py_deviceapps_xread_pb(PyObject* self, PyObject* args) {
    return bufiter_new(&BufIter_Type, args, NULL);
}


static PyMethodDef PBMethods[] = {
     {"deviceapps_xwrite_pb", py_deviceapps_xwrite_pb, METH_VARARGS, "Write serialized protobuf to file fro iterator"},
     {"deviceapps_xread_pb", py_deviceapps_xread_pb, METH_VARARGS, "Deserialize protobuf from file, return iterator"},
     {NULL, NULL, 0, NULL}
};


PyMODINIT_FUNC initpb(void) {
     (void) Py_InitModule("pb", PBMethods);
}
