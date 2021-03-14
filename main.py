import time, esp, machine, json

machine.freq(240000000)
#esp.osdebug(esp.LOG_ERROR)

class dummy:
    def alive(self):
        return False

RUNNING = True
controller_data = dummy()
bms_data = dummy()
ds_data = dummy()
calc_data = None

def controller(*args):
    from controller import KLS_S

    TARGET_RPS = 8
    PRINT_STATUS_EVERY = 5 # seconds

    global RUNNING, controller_data
    controller = KLS_S()

    count = max_work_t = 0
    min_work_t = 100000000
    loop_time = 1000 // TARGET_RPS
    next_print_fps_t = time.ticks_add(time.ticks_ms(), PRINT_STATUS_EVERY * 1000)

    while RUNNING:
        next_frame_t = time.ticks_add(time.ticks_ms(), loop_time)

        controller_data = v = controller.refresh()

        sleep_to_next_t = time.ticks_diff(next_frame_t, time.ticks_ms())
        min_work_t, max_work_t = min(max_work_t, loop_time - sleep_to_next_t), max(min_work_t, loop_time - sleep_to_next_t)
        count += 1
        time.sleep_ms(sleep_to_next_t)

        if time.ticks_diff(next_print_fps_t, time.ticks_ms()) <= 0:
            print('- CTRLR - RPS: {}, min-max time per frame: {}-{}/{}ms, comm ok:{} err:{}'.format(count / PRINT_STATUS_EVERY,
                                                          min_work_t, max_work_t, loop_time, v.comm_ok, v.comm_err))
            next_print_fps_t = time.ticks_add(time.ticks_ms(), PRINT_STATUS_EVERY * 1000)
            count = max_work_t = 0
            min_work_t = 100000000

    print('Controller thread exited')


def bms(*args):
    import bms

    TARGET_RPS = 2
    PRINT_STATUS_EVERY = 5 # seconds
    _DEVICE_MAC = b'\xa4\xc1\x38\xec\x23\xd5' # FedeBatt
    #_DEVICE_MAC = b'\xa4\xc1\x38\x07\x28\x9d' # V1.1

    global RUNNING, bms_data

    comm = bms.JBD_BMS_BLE(_DEVICE_MAC)
    bms = bms.JBD_BMS_PROTOCOL(comm)

    count = max_work_t = 0
    min_work_t = 100000000
    loop_time = 1000 // TARGET_RPS
    next_print_fps_t = time.ticks_add(time.ticks_ms(), PRINT_STATUS_EVERY * 1000)

    while RUNNING:
        next_frame_t = time.ticks_add(time.ticks_ms(), loop_time)

        bms_data = v = bms.refresh()

        sleep_to_next_t = time.ticks_diff(next_frame_t, time.ticks_ms())
        min_work_t, max_work_t = min(max_work_t, loop_time - sleep_to_next_t), max(min_work_t, loop_time - sleep_to_next_t)
        count += 1
        time.sleep_ms(sleep_to_next_t)

        if time.ticks_diff(next_print_fps_t, time.ticks_ms()) <= 0:
            print('- BMS - RPS: {}, min-max time per frame: {}-{}/{}ms, comm ok:{} err:{}'.format(count / PRINT_STATUS_EVERY,
                                                          min_work_t, max_work_t, loop_time, v.comm_ok, v.comm_err))
            next_print_fps_t = time.ticks_add(time.ticks_ms(), PRINT_STATUS_EVERY * 1000)
            count = max_work_t = 0
            min_work_t = 100000000

    comm.disconnect()
    print('BMS thread exited')


def datastore_(*args):
    import datastore1 as ds

    TARGET_RPS = 0.033 # every 30 seconds
    PRINT_STATUS_EVERY = 40 # seconds

    global RUNNING, ds_data

    ds_data = ds.DataStore(buckets=['statsA'])
    start_t = time.ticks_ms()
    run_time = 0

    count = max_work_t = 0
    min_work_t = 100000000
    loop_time = int(1000 // TARGET_RPS)
    next_print_fps_t = time.ticks_add(time.ticks_ms(), PRINT_STATUS_EVERY * 1000)

    while RUNNING:
        next_frame_t = time.ticks_add(time.ticks_ms(), loop_time)

        ds_data.persist('statsA')

        sleep_to_next_t = time.ticks_diff(next_frame_t, time.ticks_ms())
        min_work_t, max_work_t = min(max_work_t, loop_time - sleep_to_next_t), max(min_work_t, loop_time - sleep_to_next_t)
        time.sleep_ms(sleep_to_next_t)
        count += 1

        if time.ticks_diff(next_print_fps_t, time.ticks_ms()) <= 0:
            print('- DATASTORE - RPS: {}, min-max time per frame: {}-{}/{}ms'.format(count / PRINT_STATUS_EVERY,
                                                          min_work_t, max_work_t, loop_time))
            next_print_fps_t = time.ticks_add(time.ticks_ms(), PRINT_STATUS_EVERY * 1000)
            count = max_work_t = 0
            min_work_t = 100000000


def screen_main(*args):
    from screen import Screen20x4

    TARGET_RPS = 8
    PRINT_STATUS_EVERY = 5 # seconds

    global RUNNING, controller_data, bms_data, ds_data, calc_data

    screen = Screen20x4()

    count = max_work_t = 0
    min_work_t = 100000000
    loop_time = 1000 // TARGET_RPS

    count = 0
    calc_data = {'uptime': 0,
                 'power': 0,
                 'energy_count': 0}

    mark_t = time.ticks_ms()

    while RUNNING:
        ctrl_f = controller_data.alive()
        bms_f = bms_data.alive()
        ds_f = ds_data.alive()
        screen.draw_connecting(ctrl_f, bms_f, ds_f, count)
        if ctrl_f and bms_f and ds_f: break
        else: time.sleep(1)
        count += 1
    time.sleep(1)
    screen.lcd.clear()

    next_print_fps_t = time.ticks_add(time.ticks_ms(), PRINT_STATUS_EVERY * 1000)
    while RUNNING:
        next_frame_t = time.ticks_add(time.ticks_ms(), loop_time)

        screen.draw_main(controller_data, bms_data, calc_data)

        sleep_to_next_t = time.ticks_diff(next_frame_t, time.ticks_ms())
        min_work_t, max_work_t = min(max_work_t, loop_time - sleep_to_next_t), max(min_work_t, loop_time - sleep_to_next_t)
        time.sleep_ms(sleep_to_next_t)
        count += 1

        if count % 10 == 0: # every 10 iterations
            tt = time.ticks_ms()
            calc_data['uptime'] = calc_data.get('uptime', 0) + time.ticks_diff(mark_t, tt) / 1000
            mark_t = tt
            # distance travel

        if time.ticks_diff(next_print_fps_t, time.ticks_ms()) <= 0:
            print('- SCRN - RPS: {}, min-max time per frame: {}-{}/{}ms'.format(count / PRINT_STATUS_EVERY,
                                                          min_work_t, max_work_t, loop_time))
            next_print_fps_t = time.ticks_add(time.ticks_ms(), PRINT_STATUS_EVERY * 1000)
            count = max_work_t = 0
            min_work_t = 100000000

    print('Screen thread exited')


def main2():
    import _thread
    global RUNNING
    RUNNING = True

    def supervise(name, work):
        while RUNNING:
            start_time = time.ticks_ms()
            print("- SUPERVISE - starting {}".format(name))
            try:
                work()
            except KeyboardInterrupt:
                global RUNNING
                RUNNING = False
            print("- SUPERVISE - ending {} ({}s alive)".format(name, (time.ticks_ms() - start_time) / 1000))
        print('Exiting {}'.format(name))


    _thread.start_new_thread(supervise, ('controller', controller))
    _thread.start_new_thread(supervise, ('bms', bms))
    import encoder
    _thread.start_new_thread(supervise, ('encoder', encoder.test))
    _thread.start_new_thread(supervise, ('datastore', datastore_))

    try:
        screen_main()
    except KeyboardInterrupt:
        RUNNING = False
    finally:
        RUNNING = False


# import random
# def test():
#     choices = 'eduardo ole olee micropython'
#     for n in range(1000):
#     #json.dump('eduardo', open('/datastore/default', 'w'))
#         f = open('/datastore/default', 'w')
#         f.write("{}\n".format(random.choice(choices)))
#         f.flush()
#         f.close()

#         print(open('/datastore/default').read())
#         time.sleep(1)


if __name__ == "__main__":
    #main2()
    pass