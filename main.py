from __future__ import print_function

import Source as src
import Event as evnt
import Engine as eng


def fetch(startDate='2018-12-23T08:00:00Z',endDate='2018-12-29T22:00:00Z', service=None):
    # === Section 1 (Source): Read data from source === #
    # google_source = src.GoogleCalendarSource('token.json',
    #                                          'credentials.json',
    #                                          'https://www.googleapis.com/auth/calendar')

    google_source = src.GoogleO2AuthSource(service)

    # delete current schedule and upload a test schedule
    # build_test_schedule(google_source)

    instances,raw_instances = google_source.get_instances(startDate,endDate)

    # === Section 2 (User): Tag and cluster data with event type: anchor, float. for testing === #

    events = []
    for instance in instances:
        events.append(evnt.AnchorEvent(instance.title,instance.description,[instance],instance.colorId))

    retval = []
    for event in events:
        for instance in event.instances:
            retval.append(instance.to_json())

    return retval


def run(startDate='2018-12-23T08:00:00Z',endDate='2018-12-29T22:00:00Z', anchor_instances=None, floating_instances=None, service=None):
    # === Section 1 (Source): Read data from source === #
    # google_source = src.GoogleCalendarSource('token.json',
    #                                          'credentials.json',
    #                                          'https://www.googleapis.com/auth/calendar')

    google_source = src.GoogleO2AuthSource(service)

    # delete current schedule and upload a test schedule
    # build_test_schedule(google_source)

    instances,raw_instances = google_source.get_instances(startDate,endDate)

    # print("Base Instances: \n")
    # for instance in instances:
    #     instance.print()
    # print("================================================\n")

    # === Section 2 (User): Tag and cluster data with event type: anchor, float. for testing === #


    events = []
    floating_events = dict()
    for instance in instances:
        if instance.instance_id in anchor_instances:
            instance.add_event_index(len(events))
            events.append(evnt.AnchorEvent(instance.title,instance.description,[instance],instance.colorId))
        elif instance.instance_id in floating_instances:
            if instance.title in floating_events:
                instance.add_event_index(floating_events[instance.title].instances[0].event_index)
                floating_events[instance.title].add_new_instance(instance.start_time,instance.end_time,instance.event_index,instance.instance_id)
            else:
                instance.add_event_index(len(events))
                floating_events[instance.title]=evnt.FloatingEvent(instance.title,instance.description,[instance],instance.colorId)
                events.append(floating_events[instance.title])
        else:
            print("UNALLOCATED INSTANCE: " + instance.title + " , "+ instance.instance_id)


    # events = []
    # floating_events = dict()
    # for instance in instances:
    #     pref = instance.title.split("-")[0]
    #     if pref == "Anc":
    #         instance.add_event_index(len(events))
    #         events.append(evnt.AnchorEvent(instance.title,instance.description,[instance],instance.colorId))
    #     elif pref == "Flt":
    #         if instance.title in floating_events:
    #             instance.add_event_index(floating_events[instance.title].instances[0].event_index)
    #             floating_events[instance.title].add_new_instance(instance.start_time,instance.end_time,instance.event_index,instance.instance_id)
    #         else:
    #             instance.add_event_index(len(events))
    #             floating_events[instance.title]=evnt.FloatingEvent(instance.title,instance.description,[instance],instance.colorId)
    #             events.append(floating_events[instance.title])


    # === Section 3 (Calculate): Use some engine to build an optimal schedule === #

    genetic_engine = eng.GeneticEngine(events, population_size=100, elitism_factor=0.2, mutation_rate=0.2, generations=20)

    schedule = genetic_engine.run()

    retval = schedule.to_json()
    return retval
    # return schedule.to_json()

    # simulated_annealing_engine = eng.SimulatedAnnealingEngine(events)
    #
    # schedule = simulated_annealing_engine.run()

    # return schedule.to_json()

    # === Section 4 (Upload): Upload schedule to source (GUI, Calendar) === #

    # google_source.clear(raw_instances)
    # schedule.upload(google_source)


if __name__ == '__main__':
    run()