from common import *
from avatar_core.geometry import *


class HmmMapMatching:
    candidate_rid = []
    emission_dist = []
    transition_dist = []
    transition_route = []
    emission_prob = []
    transition_prob = []
    map_matching_prob = []
    brute_force_prob = []

    def __init__(self):
        pass

    def hmm_parameters(self, roadnetwork, trace, rank):
        deltas = []
        betas = []
        prev_p = None
        prev_candidates = None
        prev_road = None
        rank = int(rank)
        for p in trace.p.all():
            # find all candidate points of each point
            candidates = find_candidates_from_road(roadnetwork, p.p)
            print 'Finish calculating point candidates for sample ' + str(p.id) + '...'
            # save the emission distance and rid of each candidates
            dist_p = []
            rids_p = []
            for c in range(rank):
                dist_p.append(candidates[c][3])
                rids_p.append(candidates[c][0])
            self.emission_dist.append(dist_p)
            self.candidate_rid.append(rids_p)
            print 'Finish saving emission distance for sample ' + str(p.id) + '...'
            # save the emission distance of the nearest candidate
            nearest_road = roadnetwork.roads.get(id=candidates[0][0])
            deltas.append(candidates[0][3])
            # save the transition distance between each two points
            if prev_p is not None:
                tran_p = []
                tran_r = []
                for c in range(rank):
                    tran_diff = []
                    tran_path = []
                    for pc in range(rank):
                        current_road = roadnetwork.roads.get(id=candidates[c][0])
                        prev_road = roadnetwork.roads.get(id=prev_candidates[pc][0])
                        # route = ShortestPath.shortest_path_astar(candidates[c][1], current_road, prev_candidates[pc][1], prev_road)
                        # dist_pc = abs(Distance.earth_dist(p.p, prev_p) - route[0])
                        dist_pc = abs(Distance.earth_dist(p.p, prev_p))
                        tran_diff.append(dist_pc)
                    # tran_path.append(route[1])
                    tran_p.append(tran_diff)
                    tran_r.append(tran_path)
                self.transition_dist.append(tran_p)
                self.transition_route.append(tran_r)
                print 'Finish saving transition distance between sample ' + str(p.id) + ' and previous sample...'
                # save the transition distance between the nearest candidates of each two points
                prev_road = roadnetwork.roads.get(id=prev_candidates[0][0])
                # beta_route = ShortestPath.shortest_path_astar(candidates[0][1], nearest_road, prev_candidates[0][1], prev_road)
                # beta_p = abs(Distance.earth_dist(p.p, prev_p) - beta_route[0])
                beta_p = abs(Distance.earth_dist(p.p, prev_p))
                betas.append(beta_p)
                print 'Finish saving beta for sample ' + str(p.id) + '...'
            prev_p = p.p
            prev_candidates = candidates
            prev_road = nearest_road
        print 'Finish saving delta and beta for the entire trace...'
        print deltas
        print betas
        deltas.sort()
        betas.sort()
        delta = 1.4826 * deltas[len(deltas) / 2]
        beta = betas[len(betas) / 2] / 0.69314718
        print 'Finish calculating delta and beta...'
        return {'delta': delta, 'beta': beta}

    def hmm_prob_model(self, roadnetwork, trace, rank):
        para = self.hmm_parameters(roadnetwork, trace, rank)
        emission_para = 1.0 / (math.sqrt(2 * math.pi) * para['delta'])
        transition_para = 1.0 / para['beta']

        for zt in self.emission_dist:
            prob_t = []
            for xi in zt:
                exponent = -0.5 * (xi / para['delta']) * (xi / para['delta'])
                prob_t.append(emission_para * math.exp(exponent))
            self.emission_prob.append(prob_t)
        print 'Finish calculating eimission probabilities...'

        for zt in self.transition_dist:
            prob_dt = []
            for prev_xi in zt:
                prob_x = []
                for xi in prev_xi:
                    exponent = -xi / para['beta']
                    prob_x.append(transition_para * math.exp(exponent))
                prob_dt.append(prob_x)
            self.transition_prob.append(prob_dt)
        print 'Finish calculating transition probabilities...'

    def hmm_viterbi(self):
        chosen_index = []
        ini_prob = []
        for first in self.emission_prob[0]:
            ini_prob.append(first)
        self.map_matching_prob.append(ini_prob)
        # print len(self.transition_prob)
        # print len(self.transition_prob[0])
        # print len(self.transition_prob[0][0])
        for t in range(0, len(self.transition_prob)):
            state_prob = []
            prev_index = []
            connect_prob = []
            for current in self.transition_prob[t]:
                candidate_prob = []
                for i in range(0, len(current)):
                    value = self.map_matching_prob[t][i] * current[i] * self.emission_prob[t + 1][i]
                    candidate_prob.append(value)
                state_prob.append(max(candidate_prob))
                prev_index.append(candidate_prob.index(max(candidate_prob)))
                connect_prob.append(candidate_prob)
            chosen_index.append(prev_index)
            self.map_matching_prob.append(state_prob)
            self.brute_force_prob.append(connect_prob)
        print 'Finish forward propagation...'
        hmm_path_index = []
        hmm_path_rids = []
        # print len(chosen_index)
        # print len(self.candidate_rid)
        # print len(self.candidate_rid[0])
        final_prob = self.map_matching_prob[len(self.map_matching_prob) - 1]
        final_index = final_prob.index(max(final_prob))
        final_rid = self.candidate_rid[len(self.candidate_rid) - 1][final_index]
        current_index = final_index
        hmm_path_index.append(final_index)
        hmm_path_rids.append(final_rid)
        for i in range(len(chosen_index), 0, -1):
            prev_index = chosen_index[i - 1][hmm_path_index[len(hmm_path_rids) - 1]]
            # p_c_route = self.transition_route[current_index][prev_index]
            prev_rid = self.candidate_rid[i - 1][prev_index]
            print i - 1
            print prev_index
            # print p_c_route[0] == prev_rid
            hmm_path_index.append(prev_index)
            hmm_path_rids.append(prev_rid)
        # print len(hmm_path_rids)
        hmm_path_rids.reverse()
        return hmm_path_rids

    def perfom_map_matching(self, roadnetwork, trace, rank):
        self.hmm_prob_model(roadnetwork, trace, rank)
        print 'Finish calculating HMM model...'
        hmm_path_rids = self.hmm_viterbi()
        print 'Finish implementing viterbi algorithm...'
        hmm_path = Path(id=trace.id)
        hmm_path.save()
        prev_id = None
        path_fragment = None
        p_index = []
        for i in range(0, len(hmm_path_rids)):
            if hmm_path_rids[i] != prev_id:
                if path_fragment is not None:
                    path_fragment.p = ','.join(map(str, p_index))
                    path_fragment.save()
                    hmm_path.road.add(path_fragment)
                    p_index = []
                next_road = roadnetwork.roads.get(id=hmm_path_rids[i])
                path_fragment = PathFragment(road=next_road)
                path_fragment.save()
                prev_id = hmm_path_rids[i]
            p_index.append(i)
        hmm_path.save()
        return {'path': hmm_path, 'mm_prob': self.map_matching_prob, 'bf_prob': self.brute_force_prob}
