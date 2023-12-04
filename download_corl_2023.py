'''Downloads the metadata, paper PDFs, and the supplementary materials from OpenReview.'''

import argparse
import json
import os
from collections import defaultdict
from tqdm import tqdm
import openreview


# Needs to be modified based on the conference
CONFERENCE_NAME = 'corl23'
CONFERENCE_INVITATION = 'robot-learning.org/CoRL/2023/Conference/-/Blind_Submission'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-o', '--outdir', default='./', help='directory where data should be saved')
    parser.add_argument(
        '--get_pdfs', default=False, action='store_true', help='if included, download pdfs')
    parser.add_argument(
        '--get_supplementary', default=False, action='store_true', help='if included, download supplementary material')
    parser.add_argument(
        '--get_agreement', default=False, action='store_true', help='if included, download publication agreement')
    parser.add_argument(
        '--get_spotlight', default=False, action='store_true', help='if included, download poster spotlight')
    parser.add_argument('--baseurl', default='https://api.openreview.net')
    parser.add_argument('--username', default='', help='defaults to empty string (guest user)')
    parser.add_argument('--password', default='', help='defaults to empty string (guest user)')

    args = parser.parse_args()
    outdir = args.outdir

    # Initiates the OpenReview client.
    client = openreview.api.OpenReviewClient(
        baseurl=args.baseurl,
        username=args.username,
        password=args.password)

    # Retrieves the meta data.
    submissions = openreview.tools.iterget_notes(
        client, invitation=CONFERENCE_INVITATION)
    submissions_by_forum = {n.forum: n for n in submissions}
    metadata = []
    for forum in submissions_by_forum:
        submission_content = submissions_by_forum[forum].content
        forum_metadata = {
            'forum': forum,
            'submission_content': submission_content
        }
        # only keeps the accepted papers
        venue = submission_content['venue']
        if venue in ['CoRL 2023 Poster', 'CoRL 2023 Oral']:
            metadata.append(forum_metadata)

    outdir = os.path.join(outdir, CONFERENCE_NAME)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    print('writing metadata to file...')
    # write the metadata, one JSON per line:
    with open(os.path.join(outdir, CONFERENCE_NAME + '__metadata.jsonl'), 'w') as file_handle:
        for k, forum_metadata in enumerate(metadata):
            # print(json.dumps(forum_metadata, indent=2))
            forum = forum_metadata['forum']
            submission_content = forum_metadata['submission_content']
            title = submission_content['title']
            venue = submission_content['venue'].replace('CoRL 2023 ', '')
            print('{}\t{}\t{}\thttps://openreview.net/forum?id={}'.format(k, title, venue, forum))
            file_handle.write(json.dumps(forum_metadata) + '\n')


    # Downloads the paper PDFs.
    if args.get_pdfs:
        for forum_metadata in tqdm(metadata, desc='getting pdfs'):
            pdf_binary = client.get_pdf(forum_metadata['forum'])
            pdf_outfile = os.path.join(outdir, '{}.pdf'.format(forum_metadata['forum']))
            print("downloading {}".format(pdf_outfile))
            with open(pdf_outfile, 'wb') as file_handle:
                file_handle.write(pdf_binary)

    # Downloads the supplementary materials.
    if args.get_supplementary:
        for forum_metadata in tqdm(metadata, desc='getting supplementary materials'):
            try:
                supplementary_binary = client.get_attachment(forum_metadata['forum'], 'supplementary_material')
                supplementary_outfile = os.path.join(outdir, '{}_supp.zip'.format(forum_metadata['forum']))
                print("downloading {}".format(supplementary_outfile))
                with open(supplementary_outfile, 'wb') as file_handle:
                    file_handle.write(supplementary_binary)
            except openreview.OpenReviewException:
                print("{} not found".format(supplementary_outfile))
                print("Check {}".format(forum_metadata['submission_content']['_bibtex']))

    # Downloads the agreements.
    if args.get_agreement:
        for forum_metadata in tqdm(metadata, desc='getting publication agreements'):
            # print(json.dumps(forum_metadata, indent=2))
            try:
                agreement_binary = client.get_attachment(forum_metadata['forum'], 'publication_agreement')
                agreement_outfile = os.path.join(outdir, '{}_agreement.pdf'.format(forum_metadata['forum']))
                print("downloading {}".format(agreement_outfile))
                with open(agreement_outfile, 'wb') as file_handle:
                    file_handle.write(agreement_binary)
            except openreview.OpenReviewException:
                print("{} not found".format(agreement_outfile))
                print("Check {}".format(forum_metadata['submission_content']['_bibtex']))

    # Downloads the poster spotlights.
    if args.get_spotlight:
        for forum_metadata in tqdm(metadata, desc='getting poster spotlights'):
            venue = forum_metadata['submission_content']['venue']
            if venue not in ['CoRL 2023 Poster']: continue
            try:
                spotlight_binary = client.get_attachment(forum_metadata['forum'], 'poster_spotlight_video')
                spotlight_outfile = os.path.join(outdir, '{}_spotlight.mp4'.format(forum_metadata['forum']))
                print("downloading {}".format(spotlight_outfile))
                with open(spotlight_outfile, 'wb') as file_handle:
                    file_handle.write(spotlight_binary)
            except openreview.OpenReviewException:
                print("{} not found".format(spotlight_outfile))
                print("Check {}".format(forum_metadata['submission_content']['_bibtex']))
